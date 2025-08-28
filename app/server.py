# app/server.py
import os
import json
from typing import Optional
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from better_profanity import profanity
from openai import OpenAI

from .rag import BooksRAG
from .tools import get_summary_by_title

# ----------------------------------------------------
# Env & initialization
# ----------------------------------------------------
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

profanity.load_censor_words()

app = FastAPI(title="Smart Librarian")
rag = BooksRAG()
client = OpenAI()

# ----------------------------------------------------
# Tool (function calling) declaration for OpenAI
# ----------------------------------------------------
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_summary_by_title",
            "description": "Return the full summary for an exact book title.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Exact book title"}
                },
                "required": ["title"],
            },
        },
    }
]

# ----------------------------------------------------
# Request model
# ----------------------------------------------------
class ChatRequest(BaseModel):
    message: str
    top_k: Optional[int] = 3

# ----------------------------------------------------
# API: /chat
# ----------------------------------------------------
@app.post("/chat")
def chat(req: ChatRequest):
    user_msg = req.message.strip()

    # Optional guardrail
    if profanity.contains_profanity(user_msg):
        return {
            "assistant": "Please phrase the question politely. I can still recommend books on any topic.",
            "recommendation": None,
            "summary": None,
        }

    # 1) Retrieve context with RAG
    hits = rag.search(user_msg, k=req.top_k)
    context = "\n\n".join([f"Title: {h['title']}\nSummary: {h['summary']}" for h in hits])

    # 2) Ask the LLM; let it call our tool
    sys = (
        "You are a helpful librarian. From the context, recommend ONE best-matching book "
        "by exact Title, explain briefly why, then call the tool get_summary_by_title with that exact title."
    )

    msgs = [
        {"role": "system", "content": sys},
        {"role": "user", "content": f"User query: {user_msg}\n\nContext:\n{context}"},
    ]

    first = client.chat.completions.create(
        model=os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
        messages=msgs,
        tools=TOOLS,
        tool_choice="auto",
    )

    msg = first.choices[0].message
    recommendation_text = (msg.content or "").strip()
    full_summary = None

    # 3) Handle tool call
    if msg.tool_calls:
        for tool_call in msg.tool_calls:
            if tool_call.function.name == "get_summary_by_title":
                args = json.loads(tool_call.function.arguments or "{}")
                title = args.get("title")
                tool_result = get_summary_by_title(title)

                msgs.append(msg.model_dump(exclude_none=True))
                msgs.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": "get_summary_by_title",
                        "content": tool_result,
                    }
                )

                second = client.chat.completions.create(
                    model=os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
                    messages=msgs,
                )
                recommendation_text = (second.choices[0].message.content or "").strip()
                full_summary = tool_result
                break

    return {
        "assistant": recommendation_text,
        "recommendation": hits[0]["title"] if hits else None,
        "summary": full_summary,
    }

# ----------------------------------------------------
# Static frontend (serve index.html and assets)
# Place your frontend at: app/web/index.html
# ----------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent         # .../app
WEB_DIR = BASE_DIR / "web"                         # .../app/web
print(f"[DEBUG] Serving frontend from: {WEB_DIR}")

# 1) Serve static assets (CSS/JS/images) at /static/*
app.mount("/static", StaticFiles(directory=str(WEB_DIR)), name="static")

# 2) Serve the app shell (index.html) at /
@app.get("/")
def root():
    index_file = WEB_DIR / "index.html"
    if not index_file.exists():
        # Clear message in the API response & server logs if path is wrong
        return {"error": f"index.html not found at {index_file}"}
    return FileResponse(index_file)
