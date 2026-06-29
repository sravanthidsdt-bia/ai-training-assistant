"""Application configuration."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CORPUS_DIR = PROJECT_ROOT / "corpus"
CHROMA_DIR = PROJECT_ROOT / "data" / "chroma_db"

ROUTE_GENERAL = "general_company"
ROUTE_ROLE = "role_specific"
ROUTE_ADMIN = "admin_policy"
ROUTE_DIRECT = "direct_llm"

ROUTE_PATHS = {
    ROUTE_GENERAL: ["corpus/company"],
    ROUTE_ROLE: ["corpus/roles"],
    ROUTE_ADMIN: ["corpus/policies", "corpus/admin", "corpus/faq"],
    ROUTE_DIRECT: [],
}

ROUTE_LABELS = {
    ROUTE_GENERAL: "General Company",
    ROUTE_ROLE: "Role-Specific",
    ROUTE_ADMIN: "Administrative / Policy",
    ROUTE_DIRECT: "Direct LLM (Fallback)",
}

CHUNK_SIZE = 600
CHUNK_OVERLAP = 80
TOP_K = 4

GEMINI_MODEL = "gemini-3.5-flash"
EMBEDDING_MODEL = "default"  # ChromaDB built-in ONNX MiniLM (no torch required)

SYSTEM_PROMPT = """You are an AI Training Assistant for new employees at a fictional organization.
Your role is to help with onboarding by answering questions about company policies, roles,
administrative processes, and general company information.

Guidelines:
- Be concise, friendly, and professional.
- Ground answers ONLY in the provided context when context is available.
- If context does not contain the answer, say you don't have that information and suggest
  contacting HR, IT, or the relevant team.
- Never invent specific policy numbers, deadlines, or procedures not in the context.
- For personal or sensitive requests (salary, leave approval, performance plans), politely
  explain that you cannot access personal data or take actions, and direct the employee to
  the appropriate portal or person.
- Cite source document names when referencing policies.
"""

ROUTER_PROMPT = """Classify the employee question into exactly ONE category.

Categories:
- general_company: Company mission, values, work hours, org structure, common tools, culture
- role_specific: Job responsibilities, role expectations, team-specific workflows, career paths
- admin_policy: Expenses, leave/PTO, HR processes, IT access, timesheets, travel, compliance, onboarding steps
- direct_llm: Personal data requests, action requests (approve leave), out-of-scope topics, or questions
  that cannot be answered from internal docs (salary, tax, personal performance plans)

Respond with ONLY the category name, nothing else.

Question: {question}
Category:"""
