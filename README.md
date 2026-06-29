# AI Training Assistant for New Employees

An AI-powered onboarding assistant that routes employee questions to the right knowledge sources and generates clear, context-aware answers using **Retrieval-Augmented Generation (RAG)** and **Google Gemini**.

**Live demo:** [https://aitrainingassistant.streamlit.app](https://aitrainingassistant.streamlit.app)  
**Repository:** [https://github.com/sravanthidsdt-bia/ai-training-assistant](https://github.com/sravanthidsdt-bia/ai-training-assistant)

## Problem

New employees spend significant time searching across documents and systems for answers about company policies, roles, expenses, and administrative processes. This slows onboarding and increases dependency on HR, managers, and senior colleagues.

## Solution

This prototype accepts natural-language questions, classifies them through a **query routing decision node**, retrieves relevant context from the appropriate knowledge base, and generates grounded answers using an LLM.

### Routing Paths

| Route | Knowledge Source | Example Questions |
|-------|-----------------|-------------------|
| `general_company` | Company overview docs | Values, work hours, org structure |
| `role_specific` | Role guides | Data Analyst expectations, PM responsibilities |
| `admin_policy` | Policies, HR, IT, FAQ | Expenses, PTO, timesheets, access requests |
| `direct_llm` | No retrieval (fallback) | Salary, leave approval, personal requests |

## Architecture

```
Employee Question
       │
       ▼
┌──────────────┐
│ Router Agent │  (keyword rules + optional LLM)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Decision Node│
└──┬───┬───┬───┘
   │   │   │   │
   ▼   ▼   ▼   ▼
  Co. Role Admin Direct
   │   │   │   │
   ▼   ▼   ▼   ▼
 ChromaDB RAG (top-4 chunks)   LLM only
       │              │
       └──────┬───────┘
              ▼
      ┌───────────────┐
      │ Generator     │  (Gemini 3.5 Flash via REST API)
      └───────┬───────┘
              ▼
         Final Answer
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| LLM | Google Gemini 3.5 Flash (REST API, `x-goog-api-key` auth) |
| Embeddings | ChromaDB built-in ONNX MiniLM (local, free) |
| Vector DB | ChromaDB (persistent, metadata-filtered retrieval) |
| Backend | Python 3.10+ |
| UI | Streamlit chatbot |
| Deployment | Streamlit Cloud + GitHub |
| Orchestration | Custom multi-agent pipeline |

## Project Structure

```
├── app.py                      # Streamlit chatbot UI
├── evaluate.py                 # Evaluation against labeled test set
├── run.bat / run.ps1           # Local launchers (clear cache + start)
├── requirements.txt
├── .env.example
├── .streamlit/
│   └── secrets.toml.example    # Template for Streamlit Cloud secrets
├── corpus/                     # 13 synthetic knowledge documents
│   ├── company/
│   ├── roles/
│   ├── policies/
│   ├── admin/
│   └── faq/
├── src/
│   ├── config.py               # Settings, prompts, routes
│   ├── env_config.py           # API key loading (local + cloud)
│   ├── ingest.py               # Document chunking + embedding
│   ├── retriever.py            # ChromaDB retrieval
│   ├── router.py               # Hybrid query classification
│   ├── generator.py            # Gemini REST API response generation
│   └── assistant.py            # Main orchestrator
├── docs/
│   ├── TECHNICAL_REPORT.md
│   ├── PRESENTATION.md
│   └── JURY_WRITEUP.md         # End-to-end project explanation
├── evaluation_set.csv            # 20 labeled test questions
└── data/chroma_db/               # Vector store (auto-generated, gitignored)
```

## Local Setup

### 1. Prerequisites

- Python 3.10 or higher
- A [Google Gemini API key](https://aistudio.google.com/apikey) (supports `AIza` and `AQ.` key formats)

### 2. Install Dependencies

```powershell
cd "AI training assistant -CUR"
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure API Key (local only)

```powershell
copy .env.example .env
```

Edit `.env`:

```
GEMINI_API_KEY=your_actual_key_here
```

**Never commit `.env` to GitHub.**

### 4. Build the Knowledge Base

```powershell
python -m src.ingest
```

Indexes 68 document chunks into ChromaDB.

### 5. Run the Chatbot

```powershell
.\run.bat
```

Or: `venv\Scripts\streamlit run app.py`

## Streamlit Cloud Deployment

1. Push code to GitHub (repo connected to Streamlit Cloud)
2. In [share.streamlit.io](https://share.streamlit.io) → your app → **Settings** → **Secrets**, add:

```toml
GEMINI_API_KEY = "your_actual_key_here"
```

3. Reboot the app
4. Click **Build Knowledge Base** in the sidebar on first run

**Do not put API keys in GitHub** — use Streamlit Secrets only.

## Evaluation

```powershell
python evaluate.py
```

Runs 20 labeled questions and reports routing accuracy to `evaluation_results.csv`.

## Example Questions

| Question | Route |
|----------|-------|
| "What are the company's core values?" | `general_company` |
| "As a Data Analyst, what are the first 30 days expectations?" | `role_specific` |
| "How do I submit an expense claim?" | `admin_policy` |
| "What is my exact salary breakup?" | `direct_llm` (refusal/redirect) |

## Documentation

- [Technical Report](docs/TECHNICAL_REPORT.md) — Architecture, routing, RAG, prompts, deployment
- [Presentation](docs/PRESENTATION.md) — Slide deck for capstone presentation
- [Jury Writeup](docs/JURY_WRITEUP.md) — End-to-end project walkthrough for evaluation

## Author

Capstone project — AI Training Assistant for New Employees.
