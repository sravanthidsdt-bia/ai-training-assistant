"""LLM response generation using Google Gemini REST API."""

from __future__ import annotations

import os

import httpx
from dotenv import load_dotenv

from src.config import PROJECT_ROOT, SYSTEM_PROMPT

load_dotenv(PROJECT_ROOT / ".env", override=True)

GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta"

# Hardcoded Gemini model for API calls
ACTIVE_GEMINI_MODEL = "gemini-3.5-flash"


def _get_model() -> str:
    return ACTIVE_GEMINI_MODEL

DIRECT_LLM_PROMPT = """The employee asked a question that cannot be answered from internal documents.
This may involve personal data, action requests, or out-of-scope topics.

Employee question: {question}

Respond helpfully but:
- Do NOT invent personal information (salary, leave balance, etc.)
- Do NOT pretend to approve requests or access private systems
- Politely explain limitations and direct them to HR portal, manager, or IT as appropriate
- If they need a template or general guidance (e.g., performance plan structure), provide generic help
  while clarifying you don't have their specific context
"""

RAG_PROMPT = """Use the following internal documents to answer the employee's question.
If the answer is not in the context, say so and suggest who to contact.

Context:
{context}

Employee question: {question}

Provide a clear, concise answer. Mention relevant policy names or document sources when applicable.
"""


class LLMGenerator:
    """Generate responses via Gemini REST API (supports AQ. auth keys)."""

    def __init__(self, api_key: str | None = None) -> None:
        key = (api_key or os.getenv("GEMINI_API_KEY") or "").strip()
        if not key:
            raise ValueError(
                "GEMINI_API_KEY not set. Add it to .env — get a key at "
                "https://aistudio.google.com/apikey"
            )
        self._api_key = key

    def _call_api(self, prompt: str) -> str:
        """Call Gemini generateContent with x-goog-api-key (native auth for AQ. keys)."""
        model = _get_model()
        url = f"{GEMINI_API_BASE}/models/{model}:generateContent"
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self._api_key,
        }
        payload = {
            "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        }

        with httpx.Client(timeout=90.0) as client:
            response = client.post(url, headers=headers, json=payload)

        if response.status_code == 401:
            raise ValueError(
                "Gemini API authentication failed (401). Check GEMINI_API_KEY in .env. "
                "Create or verify your key at https://aistudio.google.com/apikey"
            )

        if response.status_code == 404:
            detail = response.text[:200]
            raise ValueError(
                f"Gemini model '{model}' not available (404). "
                f"Using model: {model}. API says: {detail}"
            )

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise ValueError(
                f"Gemini API error ({exc.response.status_code}): {exc.response.text[:300]}"
            ) from exc

        data = response.json()

        try:
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except (KeyError, IndexError, TypeError) as exc:
            raise ValueError(f"Unexpected Gemini API response: {data}") from exc

    def generate_raw(self, prompt: str) -> str:
        """Generate a raw text response (used by router)."""
        return self._call_api(prompt)

    def generate_rag_answer(self, question: str, context: str) -> str:
        """Generate an answer grounded in retrieved context."""
        prompt = RAG_PROMPT.format(context=context, question=question)
        return self.generate_raw(prompt)

    def generate_direct_answer(self, question: str) -> str:
        """Generate a fallback answer without RAG context."""
        prompt = DIRECT_LLM_PROMPT.format(question=question)
        return self.generate_raw(prompt)
