"""Streamlit chatbot UI for the AI Training Assistant."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv(PROJECT_ROOT / ".env", override=True)

# Bust stale src modules (OneDrive / Streamlit hot-reload can serve old code)
for _mod in list(sys.modules):
    if _mod == "src" or _mod.startswith("src."):
        del sys.modules[_mod]

from src.config import CHROMA_DIR, ROUTE_LABELS
from src.env_config import api_key_help_text, load_gemini_api_key

load_gemini_api_key()

# Hardcoded model — do not read from env/cache
ACTIVE_GEMINI_MODEL = "gemini-3.5-flash"

# Bump to force Streamlit to drop cached assistant after code changes
ASSISTANT_VERSION = "hardcoded-gemini-3.5-v7"

VENV_PYTHON = PROJECT_ROOT / "venv" / "Scripts" / "python.exe"


def _check_environment() -> str | None:
    """Return an error message if the runtime environment is misconfigured."""
    if not VENV_PYTHON.exists():
        return None

    if Path(sys.executable).resolve() != VENV_PYTHON.resolve():
        return (
            "This app is running with system Python instead of the project virtual "
            "environment. Activate the venv first, or run:\n\n"
            "`venv\\Scripts\\streamlit run app.py`"
        )

    try:
        import httpx  # noqa: F401
    except ModuleNotFoundError:
        return (
            "Missing dependencies. Run:\n\n"
            "`venv\\Scripts\\pip install -r requirements.txt`"
        )

    return None

st.set_page_config(
    page_title="AI Training Assistant",
    page_icon="🎓",
    layout="wide",
)

st.markdown(
    """
    <style>
    .route-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 8px;
    }
    .route-general { background: #e3f2fd; color: #1565c0; }
    .route-role { background: #f3e5f5; color: #7b1fa2; }
    .route-admin { background: #e8f5e9; color: #2e7d32; }
    .route-direct { background: #fff3e0; color: #e65100; }
    </style>
    """,
    unsafe_allow_html=True,
)

ROUTE_CSS = {
    "general_company": "route-general",
    "role_specific": "route-role",
    "admin_policy": "route-admin",
    "direct_llm": "route-direct",
}

EXAMPLE_QUESTIONS = [
    "What are the company's core values?",
    "As a Data Analyst, what are the first 30 days expectations?",
    "How do I submit an expense claim?",
    "How do I request PTO?",
    "What is my exact salary breakup?",
]


def init_session():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    # Drop cached assistant when code/SDK version changes (fixes stale SDK in memory)
    if st.session_state.get("assistant_version") != ASSISTANT_VERSION:
        st.session_state.assistant = None
        st.session_state.assistant_version = ASSISTANT_VERSION
    elif "assistant" not in st.session_state:
        st.session_state.assistant = None


def get_assistant():
    env_error = _check_environment()
    if env_error:
        return None, env_error

    if not load_gemini_api_key():
        return None, None

    try:
        from src.assistant import TrainingAssistant

        return TrainingAssistant(), None
    except FileNotFoundError:
        return None, None


def main():
    init_session()

    env_error = _check_environment()

    with st.sidebar:
        st.title("🎓 Training Assistant")
        st.markdown("AI-powered onboarding helper for new employees.")
        st.divider()

        if not CHROMA_DIR.exists():
            st.warning("Vector DB not built yet.")
            if st.button("Build Knowledge Base"):
                with st.spinner("Indexing documents..."):
                    from src.ingest import ingest

                    count = ingest()
                    st.success(f"Indexed {count} chunks!")
                    st.rerun()
        else:
            st.success("Knowledge base ready")

        if env_error:
            st.error(env_error)
        elif not load_gemini_api_key():
            st.error("Gemini API key not configured")
            st.markdown(api_key_help_text())
            st.markdown("[Get a free API key](https://aistudio.google.com/apikey)")
        else:
            st.caption(f"Model: `{ACTIVE_GEMINI_MODEL}`")
            st.success("Gemini API connected")

        st.divider()
        st.markdown("**Try these questions:**")
        for q in EXAMPLE_QUESTIONS:
            if st.button(q, key=f"ex_{q[:20]}", use_container_width=True):
                st.session_state.pending_question = q

        st.divider()
        if st.button("Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.assistant = None
            st.rerun()

        with st.expander("Routing Paths"):
            for key, label in ROUTE_LABELS.items():
                st.markdown(f"- **{label}** → `{key}`")

    st.title("AI Training Assistant")
    st.caption(
        "Ask about company policies, your role, HR processes, and onboarding steps."
    )

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("meta"):
                meta = msg["meta"]
                css = ROUTE_CSS.get(meta["route"], "")
                st.markdown(
                    f'<span class="route-badge {css}">'
                    f'📍 {meta["route_label"]} · {meta["routing_method"]}'
                    f"</span>",
                    unsafe_allow_html=True,
                )
                if meta.get("sources"):
                    with st.expander("Sources"):
                        for s in meta["sources"]:
                            st.markdown(
                                f"- **{s['doc_name']}** — {s['section']} "
                                f"(relevance: {s['score']})"
                            )

    pending = st.session_state.pop("pending_question", None)
    user_input = pending or st.chat_input("Ask a question about onboarding...")

    if user_input:
        st.session_state.messages.append(
            {"role": "user", "content": user_input}
        )
        with st.chat_message("user"):
            st.markdown(user_input)

        assistant, _ = get_assistant()
        if assistant is None:
            with st.chat_message("assistant"):
                if env_error:
                    st.error(env_error)
                elif not CHROMA_DIR.exists():
                    st.error(
                        "Knowledge base not built. "
                        "Click 'Build Knowledge Base' in the sidebar."
                    )
                else:
                    st.error("Gemini API key not configured.")
                    st.markdown(api_key_help_text())
        else:
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        result = assistant.ask(user_input)
                    except Exception as exc:
                        st.error(f"Gemini API error: {exc}")
                        st.stop()

                st.markdown(result["answer"])
                css = ROUTE_CSS.get(result["route"], "")
                st.markdown(
                    f'<span class="route-badge {css}">'
                    f'📍 {result["route_label"]} · {result["routing_method"]}'
                    f"</span>",
                    unsafe_allow_html=True,
                )

                if result.get("sources"):
                    with st.expander("Sources"):
                        for s in result["sources"]:
                            st.markdown(
                                f"- **{s['doc_name']}** — {s['section']} "
                                f"(relevance: {s['score']})"
                            )

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": result["answer"],
                        "meta": result,
                    }
                )


if __name__ == "__main__":
    main()
