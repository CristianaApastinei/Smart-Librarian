# app/rag.py
import os
from pathlib import Path
import chromadb
from chromadb.config import Settings
from openai import OpenAI

DB_DIR = Path(__file__).resolve().parents[1] / "chroma_db"

# Use the same model you used at ingest time
EMBED_MODEL = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")

class BooksRAG:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=str(DB_DIR), settings=Settings())
        self.col = self.client.get_collection("book_summaries")
        self._openai = OpenAI()

    def _embed(self, text: str):
        # Create ONE embedding that matches the ingested vectors' dimension
        resp = self._openai.embeddings.create(model=EMBED_MODEL, input=[text])
        return resp.data[0].embedding

    def search(self, query: str, k: int = 3):
        q_emb = self._embed(query)
        # IMPORTANT: pass query_embeddings (NOT query_texts) so the dims match
        res = self.col.query(
            query_embeddings=[q_emb],
            n_results=k,
            include=["documents", "metadatas", "distances"]
        )
        docs = []
        for i in range(len(res["documents"][0])):
            docs.append({
                "title": res["metadatas"][0][i]["title"],
                "summary": res["documents"][0][i],
                "score": res["distances"][0][i]
            })
        return docs
