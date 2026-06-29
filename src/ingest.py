"""Document ingestion: load corpus, chunk, and embed into ChromaDB."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

from src.config import CHROMA_DIR, CHUNK_OVERLAP, CHUNK_SIZE, CORPUS_DIR


def _chunk_text(text: str, source: str) -> list[dict]:
    """Split markdown into overlapping chunks with section metadata."""
    chunks: list[dict] = []
    sections = re.split(r"(?=^## )", text, flags=re.MULTILINE)

    for section in sections:
        section = section.strip()
        if not section:
            continue

        header_match = re.match(r"^## (.+)$", section, re.MULTILINE)
        section_title = header_match.group(1).strip() if header_match else "Introduction"

        paragraphs = [p.strip() for p in section.split("\n\n") if p.strip()]
        current = ""

        for para in paragraphs:
            if len(current) + len(para) + 2 <= CHUNK_SIZE:
                current = f"{current}\n\n{para}".strip() if current else para
            else:
                if current:
                    chunks.append(
                        {
                            "text": current,
                            "section": section_title,
                            "source": source,
                        }
                    )
                if len(para) <= CHUNK_SIZE:
                    current = para
                else:
                    for i in range(0, len(para), CHUNK_SIZE - CHUNK_OVERLAP):
                        piece = para[i : i + CHUNK_SIZE]
                        chunks.append(
                            {
                                "text": piece,
                                "section": section_title,
                                "source": source,
                            }
                        )
                    current = ""

        if current:
            chunks.append(
                {
                    "text": current,
                    "section": section_title,
                    "source": source,
                }
            )

    return chunks


def _route_for_source(rel_path: str) -> str:
    """Map a corpus file path to its knowledge route."""
    if rel_path.startswith("corpus/company"):
        return "general_company"
    if rel_path.startswith("corpus/roles"):
        return "role_specific"
    return "admin_policy"


def load_documents(corpus_dir: Path | None = None) -> list[dict]:
    """Load all markdown files from the corpus."""
    root = corpus_dir or CORPUS_DIR
    documents: list[dict] = []

    for md_file in sorted(root.rglob("*.md")):
        rel_path = md_file.relative_to(root.parent).as_posix()
        text = md_file.read_text(encoding="utf-8")
        route = _route_for_source(rel_path)

        for chunk in _chunk_text(text, rel_path):
            chunk["route"] = route
            chunk["doc_name"] = md_file.name
            documents.append(chunk)

    return documents


def ingest(corpus_dir: Path | None = None, reset: bool = True) -> int:
    """Ingest corpus into ChromaDB. Returns number of chunks indexed."""
    import chromadb
    from chromadb.utils import embedding_functions

    documents = load_documents(corpus_dir)
    if not documents:
        raise ValueError(f"No documents found in corpus at {CORPUS_DIR}")

    if reset and CHROMA_DIR.exists():
        import shutil

        shutil.rmtree(CHROMA_DIR)

    CHROMA_DIR.mkdir(parents=True, exist_ok=True)

    ef = embedding_functions.DefaultEmbeddingFunction()
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.get_or_create_collection(
        name="training_assistant",
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )

    ids, texts, metadatas = [], [], []
    for doc in documents:
        doc_id = hashlib.md5(
            f"{doc['source']}:{doc['section']}:{doc['text'][:80]}".encode()
        ).hexdigest()
        ids.append(doc_id)
        texts.append(doc["text"])
        metadatas.append(
            {
                "source": doc["source"],
                "section": doc["section"],
                "route": doc["route"],
                "doc_name": doc["doc_name"],
            }
        )

    batch_size = 50
    for i in range(0, len(ids), batch_size):
        collection.add(
            ids=ids[i : i + batch_size],
            documents=texts[i : i + batch_size],
            metadatas=metadatas[i : i + batch_size],
        )

    return len(documents)


if __name__ == "__main__":
    count = ingest()
    print(f"Ingested {count} chunks into {CHROMA_DIR}")
