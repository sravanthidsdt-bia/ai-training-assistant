# AI Training Assistant for New Employees

An AI-powered onboarding assistant that routes employee questions to the right knowledge sources and generates clear, context-aware answers using **Retrieval-Augmented Generation (RAG)** and **Google Gemini**.

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
│ Router Agent │  (LLM + keyword rules)
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
 ChromaDB RAG (top-k chunks)   LLM only
       │              │
       └──────┬───────┘
              ▼
      ┌───────────────┐
      │ Generator     │  (Google Gemini)
      │ (LLM + context)│
      └───────┬───────┘
              ▼
         Final Answer
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| LLM | Google Gemini 3.5 Flash (free API tier) |
| Embeddings | ChromaDB built-in ONNX MiniLM (local, free) |
| Vector DB | ChromaDB (local, persistent) |
| Backend | Python 3.10+ |
| UI | Streamlit chatbot |
| Orchestration | Custom multi-agent pipeline |

## Project Structure

```
├── app.py                  # Streamlit chatbot UI
├── evaluate.py             # Run evaluation against labeled test set
├── requirements.txt
├── .env.example
├── corpus/                 # Synthetic knowledge documents
│   ├── company/
│   ├── roles/
│   ├── policies/
│   ├── admin/
│   └── faq/
├── src/
│   ├── config.py           # Settings and prompts
│   ├── ingest.py           # Document chunking + embedding
│   ├── retriever.py        # ChromaDB retrieval
│   ├── router.py           # Query classification
│   ├── generator.py        # Gemini response generation
│   └── assistant.py        # Main orchestrator
├── docs/
│   ├── TECHNICAL_REPORT.md
│   └── PRESENTATION.md
├── evaluation_set.csv      # 20 labeled test questions
└── data/chroma_db/         # Vector store (auto-generated)
```

## Setup

### 1. Prerequisites

- Python 3.10 or higher
- A free [Google Gemini API key](https://aistudio.google.com/apikey)

### 2. Install Dependencies

```bash
cd "AI training assistant -CUR"
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure API Key

```bash
copy .env.example .env
```

Edit `.env` and set your Gemini API key:

```
GEMINI_API_KEY=your_actual_key_here
```

### 4. Build the Knowledge Base

```bash
python -m src.ingest
```

This chunks all markdown documents in `corpus/`, embeds them, and stores them in ChromaDB.

### 5. Run the Chatbot

**Option A — use the launcher (recommended on Windows):**

```powershell
.\run.bat
```

**Option B — activate venv manually:**

```powershell
venv\Scripts\activate
streamlit run app.py
```

**Option C — call venv streamlit directly (no activation needed):**

```powershell
venv\Scripts\streamlit run app.py
```

Open the URL shown in the terminal (typically `http://localhost:8501`).

## Evaluation

Run the assistant against the 20-question labeled evaluation set:

```bash
python evaluate.py
```

This reports routing accuracy and saves detailed results to `evaluation_results.csv`.

## Example Questions

- "What are the company's core values?" → `general_company`
- "As a Data Analyst, what are the first 30 days expectations?" → `role_specific`
- "How do I submit an expense claim?" → `admin_policy`
- "What is my exact salary breakup?" → `direct_llm` (refusal/redirect)

## Documentation

- [Technical Report](docs/TECHNICAL_REPORT.md) — Architecture, routing design, prompts, limitations
- [Presentation](docs/PRESENTATION.md) — Slide deck content for project presentation

## License

Educational / capstone project. Corpus documents are synthetic and fictional.
