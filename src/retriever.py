"""Vector retrieval over ChromaDB knowledge bases."""

from __future__ import annotations

import chromadb
from chromadb.utils import embedding_functions

from src.config import CHROMA_DIR, ROUTE_ADMIN, TOP_K


class DocumentRetriever:
    """Retrieve relevant document chunks filtered by route."""

    def __init__(self) -> None:
        if not CHROMA_DIR.exists():
            raise FileNotFoundError(
                f"Vector database not found at {CHROMA_DIR}. "
                "Run: python -m src.ingest"
            )

        ef = embedding_functions.DefaultEmbeddingFunction()
        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        self._collection = client.get_collection(
            name="training_assistant",
            embedding_function=ef,
        )

    def retrieve(
        self,
        query: str,
        route: str,
        top_k: int = TOP_K,
    ) -> list[dict]:
        """Retrieve top-k chunks for a query within a route's knowledge base."""
        if route == ROUTE_ADMIN:
            where_filter = {
                "$or": [
                    {"route": {"$eq": "admin_policy"}},
                ]
            }
        else:
            where_filter = {"route": {"$eq": route}}

        results = self._collection.query(
            query_texts=[query],
            n_results=top_k,
            where=where_filter,
            include=["documents", "metadatas", "distances"],
        )

        chunks: list[dict] = []
        if not results["documents"] or not results["documents"][0]:
            return chunks

        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            chunks.append(
                {
                    "text": doc,
                    "source": meta.get("source", ""),
                    "section": meta.get("section", ""),
                    "doc_name": meta.get("doc_name", ""),
                    "score": round(1 - dist, 3),
                }
            )

        return chunks

    def format_context(self, chunks: list[dict]) -> str:
        """Format retrieved chunks into a context block for the LLM."""
        if not chunks:
            return "No relevant documents found."

        parts = []
        for i, chunk in enumerate(chunks, 1):
            parts.append(
                f"[Source {i}: {chunk['doc_name']} — {chunk['section']}]\n"
                f"{chunk['text']}"
            )
        return "\n\n---\n\n".join(parts)
