"""Query classification and routing logic."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from src.config import (
    ROUTE_ADMIN,
    ROUTE_DIRECT,
    ROUTE_GENERAL,
    ROUTE_ROLE,
    ROUTER_PROMPT,
)

if TYPE_CHECKING:
    from src.generator import LLMGenerator


class QueryRouter:
    """Route employee questions to the appropriate knowledge source."""

    VALID_ROUTES = {ROUTE_GENERAL, ROUTE_ROLE, ROUTE_ADMIN, ROUTE_DIRECT}

    KEYWORD_RULES: list[tuple[str, list[str]]] = [
        (
            ROUTE_ROLE,
            [
                r"\bdata analyst\b",
                r"\bproduct manager\b",
                r"\bmy role\b",
                r"\bfirst 30 days\b",
                r"\bresponsibilit",
                r"\bwho (should|to) (i )?ask\b",
                r"\bteam\b",
                r"\bjob\b",
            ],
        ),
        (
            ROUTE_ADMIN,
            [
                r"\bexpense",
                r"\breimburs",
                r"\bpto\b",
                r"\bleave\b",
                r"\btimesheet",
                r"\bhr\b",
                r"\bit ticket",
                r"\baccess request",
                r"\bsecurity incident",
                r"\btravel\b",
                r"\bonboarding\b",
                r"\bcompliance\b",
                r"\bcode of conduct\b",
                r"\bverification letter\b",
            ],
        ),
        (
            ROUTE_GENERAL,
            [
                r"\bcompany\b",
                r"\bvalues\b",
                r"\bmission\b",
                r"\bwork hours\b",
                r"\borg\b",
                r"\bculture\b",
                r"\bcommon tools\b",
                r"\bcollaboration window\b",
            ],
        ),
        (
            ROUTE_DIRECT,
            [
                r"\bmy salary\b",
                r"\bsalary breakup\b",
                r"\btax deduction",
                r"\bapprove my leave\b",
                r"\bperformance improvement plan\b",
                r"\bpersonal payroll\b",
            ],
        ),
    ]

    def __init__(self, llm: LLMGenerator | None = None) -> None:
        self._llm = llm

    def _keyword_route(self, question: str) -> str | None:
        """Fast keyword-based routing fallback."""
        q = question.lower()
        scores: dict[str, int] = {r: 0 for r in self.VALID_ROUTES}

        for route, patterns in self.KEYWORD_RULES:
            for pattern in patterns:
                if re.search(pattern, q):
                    scores[route] += 1

        best = max(scores, key=scores.get)
        if scores[best] > 0:
            return best
        return None

    def _llm_route(self, question: str) -> str:
        """LLM-based query classification."""
        prompt = ROUTER_PROMPT.format(question=question)
        response = self._llm.generate_raw(prompt).strip().lower()

        for route in self.VALID_ROUTES:
            if route in response:
                return route

        return ROUTE_ADMIN

    def route(self, question: str, use_llm: bool = True) -> dict:
        """
        Classify a question and return routing metadata.

        Uses a hybrid approach: keyword rules for high-confidence cases,
        LLM classification when available, with admin_policy as default.
        """
        keyword_result = self._keyword_route(question)

        if keyword_result == ROUTE_DIRECT:
            return self._build_result(question, ROUTE_DIRECT, "keyword", 0.95)

        if keyword_result:
            return self._build_result(question, keyword_result, "keyword", 0.75)

        if use_llm and self._llm:
            try:
                llm_result = self._llm_route(question)
                return self._build_result(question, llm_result, "llm", 0.85)
            except Exception:
                pass

        return self._build_result(question, ROUTE_ADMIN, "default", 0.5)

    @staticmethod
    def _build_result(
        question: str, route: str, method: str, confidence: float
    ) -> dict:
        return {
            "question": question,
            "route": route,
            "method": method,
            "confidence": confidence,
        }
