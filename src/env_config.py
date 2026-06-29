"""Load API keys from environment or Streamlit Cloud secrets."""

from __future__ import annotations

import os


def load_gemini_api_key() -> str | None:
    """Read GEMINI_API_KEY from env or Streamlit secrets (for cloud deploy)."""
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if key:
        return key

    try:
        import streamlit as st

        secret = st.secrets.get("GEMINI_API_KEY", "")
        if secret:
            key = str(secret).strip()
            os.environ["GEMINI_API_KEY"] = key
            return key
    except Exception:
        pass

    return None


def api_key_help_text() -> str:
    """Instructions shown when the API key is missing."""
    return (
        "**Local:** add `GEMINI_API_KEY` to your `.env` file.\n\n"
        "**Streamlit Cloud:** open [share.streamlit.io](https://share.streamlit.io) → "
        "your app → **Settings** → **Secrets**, and add:\n\n"
        "```toml\nGEMINI_API_KEY = \"your_key_here\"\n```\n\n"
        "Do **not** put API keys in GitHub."
    )
