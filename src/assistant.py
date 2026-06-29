"""Main orchestration: route → retrieve → generate."""

from __future__ import annotations

from src.config import ROUTE_DIRECT, ROUTE_LABELS
from src.generator import LLMGenerator
from src.retriever import DocumentRetriever
from src.router import QueryRouter


class TrainingAssistant:
    """
    AI Training Assistant orchestrator.

    Pipeline:
      1. Router Agent  — classifies the query
      2. Decision Node — selects knowledge source path
      3. Retriever     — fetches relevant chunks (RAG routes only)
      4. Generator     — produces the final answer
    """

    def __init__(self, api_key: str | None = None) -> None:
        self.llm = LLMGenerator(api_key=api_key)
        self.router = QueryRouter(llm=self.llm)
        self.retriever = DocumentRetriever()

    def ask(self, question: str) -> dict:
        """Process an employee question end-to-end."""
        routing = self.router.route(question)
        route = routing["route"]

        result = {
            "question": question,
            "route": route,
            "route_label": ROUTE_LABELS.get(route, route),
            "routing_method": routing["method"],
            "confidence": routing["confidence"],
            "sources": [],
            "answer": "",
        }

        if route == ROUTE_DIRECT:
            result["answer"] = self.llm.generate_direct_answer(question)
            return result

        chunks = self.retriever.retrieve(question, route)
        context = self.retriever.format_context(chunks)
        result["sources"] = [
            {
                "doc_name": c["doc_name"],
                "section": c["section"],
                "score": c["score"],
            }
            for c in chunks
        ]
        result["answer"] = self.llm.generate_rag_answer(question, context)
        return result
