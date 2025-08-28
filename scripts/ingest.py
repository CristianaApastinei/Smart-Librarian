import os, re, uuid
from pathlib import Path
import chromadb
from chromadb.config import Settings
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


DATA = Path(__file__).resolve().parents[1] / "data" / "book_summaries.md"
DB_DIR = Path(__file__).resolve().parents[1] / "chroma_db"

def parse_markdown(md_text: str):
    chunks = re.split(r"^## Title:\s*", md_text, flags=re.M)
    books = []
    for ch in chunks:
        ch = ch.strip()
        if not ch: continue
        title, *body = ch.splitlines()
        summary = "\n".join(body).strip()
        books.append({"title": title.strip(), "summary": summary})
    return books

def embed_texts(texts):
    resp = client.embeddings.create(
        model="text-embedding-3-small",  # OpenAI embeddings model
        input=texts
    )
    return [d.embedding for d in resp.data]

def main():
    md = DATA.read_text(encoding="utf-8")
    books = parse_markdown(md)

    # Persistent Chroma client
    chroma = chromadb.PersistentClient(path=str(DB_DIR), settings=Settings(allow_reset=True))
    try:
        chroma.delete_collection("book_summaries")
    except Exception:
        pass
    col = chroma.create_collection(name="book_summaries")  # or get_or_create_collection

    docs = [b["summary"] for b in books]
    ids = [str(uuid.uuid4()) for _ in books]
    metas = [{"title": b["title"]} for b in books]

    embs = embed_texts([f'{b["title"]}\n{b["summary"]}' for b in books])
    col.add(documents=docs, metadatas=metas, embeddings=embs, ids=ids)
    print(f"Ingested {len(books)} books into Chroma at {DB_DIR}")

if __name__ == "__main__":
    main()
