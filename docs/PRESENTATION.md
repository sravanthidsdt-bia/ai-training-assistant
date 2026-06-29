# AI Training Assistant — Presentation Deck

> Each `---` separator represents a new slide.

---

## Slide 1: Title

# AI Training Assistant for New Employees

**Capstone Project — Sravanthi**

An intelligent onboarding assistant that routes questions to the right knowledge sources and generates context-aware answers.

**Live Demo:** [aitrainingassistant.streamlit.app](https://aitrainingassistant.streamlit.app)

---

## Slide 2: The Problem

# Onboarding Challenges

- New employees search across **multiple documents and systems**
- Routine questions go to **HR, managers, and senior colleagues**
- Slow ramp-up during the **first 30–90 days**
- Missed deadlines on expenses, timesheets, and access requests
- **Inconsistent answers** depending on who you ask

> *"Where do I submit expenses? Who approves my leave? What are my first-month goals?"*

---

## Slide 3: Our Solution

# AI-Powered Training Assistant

A chatbot that:

1. Accepts questions in **natural language**
2. **Routes** queries to the right knowledge source
3. **Retrieves** relevant policy and role documents (RAG)
4. **Generates** clear, grounded answers with citations

**Result:** Self-service onboarding support available 24/7

---

## Slide 4: System Architecture

# Architecture Overview

```
Employee → Router Agent → Decision Node → Knowledge Base → Generator → Answer
                │              │
                │         ┌────┴────┐
                │         │ 4 Paths │
                │         └────┬────┘
                │    ┌────┬────┼────┐
                │    ▼    ▼    ▼    ▼
                │  Co. Role Admin Direct
                │    │    │    │    │
                │    └────┴────┘    │
                │         │         │
                │    ChromaDB RAG   LLM Only
                │         │         │
                └─────────┴─────────┘
                          ▼
                  Gemini 3.5 Flash
                  (REST API)
```

---

## Slide 5: Query Routing

# Intelligent Query Routing

| Route | Handles | Example |
|-------|---------|---------|
| **General Company** | Values, hours, tools | "What are our core values?" |
| **Role-Specific** | Job expectations | "First 30 days as Data Analyst?" |
| **Admin / Policy** | HR, IT, expenses, PTO | "How do I submit expenses?" |
| **Direct LLM** | Personal / out-of-scope | "What is my salary?" |

**Hybrid routing:** Keyword rules (fast, safe) + LLM classification (nuanced)

---

## Slide 6: Knowledge Sources

# Multi-Source Knowledge Base

**13 synthetic documents** across 5 categories:

- **Company** — Mission, values, work model
- **Roles** — Data Analyst, Product Manager guides
- **Policies** — Expense, leave, conduct, security
- **Admin** — HR processes, IT access, timesheets, travel
- **FAQ** — Common onboarding questions

→ **68 chunks** indexed in ChromaDB with semantic embeddings

---

## Slide 7: RAG Pipeline

# Retrieval-Augmented Generation

1. **Chunk** documents by section (600 chars, 80 overlap)
2. **Embed** with ChromaDB ONNX MiniLM (local, free, no GPU)
3. **Store** in ChromaDB with route metadata
4. **Retrieve** top-4 relevant chunks per query (route-filtered)
5. **Generate** answer with Gemini 3.5 Flash using retrieved context

> Answers are **grounded in real documents**, not hallucinated.

---

## Slide 8: LLM Integration

# Google Gemini 3.5 Flash

| Aspect | Detail |
|--------|--------|
| Model | `gemini-3.5-flash` |
| Integration | REST API via `httpx` |
| Auth | `x-goog-api-key` header (supports `AQ.` keys) |
| System prompt | Role, tone, grounding rules |
| RAG prompt | Context + question → cited answer |

Why REST API? Newer Google auth keys (`AQ.` prefix) require native API authentication.

---

## Slide 9: Demo Scenarios

# Live Demo Scenarios

| # | Question | Route | Behavior |
|---|----------|-------|----------|
| 1 | "What are the company's core values?" | General Company | RAG + citations |
| 2 | "First 30 days as a Data Analyst?" | Role-Specific | RAG + citations |
| 3 | "How do I submit an expense claim?" | Admin / Policy | RAG + citations |
| 4 | "What is my exact salary breakup?" | Direct LLM | Polite refusal |

Each answer shows a **route badge** and **source citations**.

**Try it:** [aitrainingassistant.streamlit.app](https://aitrainingassistant.streamlit.app)

---

## Slide 10: Fallback Handling

# Graceful Fallbacks

When the assistant **cannot** answer from documents:

- **Personal data** (salary, tax) → Redirect to HR payroll
- **Action requests** (approve leave) → Explain limitations; point to portal
- **Missing information** → Admit gap; suggest contacting the right team
- **Sensitive topics** → Professional refusal with escalation path

No hallucinated policies. No fake approvals.

---

## Slide 11: Tech Stack

# Technology Choices

| Layer | Technology | Why |
|-------|-----------|-----|
| LLM | Gemini 3.5 Flash | Fast, capable, free API tier |
| API | REST + httpx | Supports new `AQ.` auth keys |
| Embeddings | ChromaDB ONNX MiniLM | Local, no API cost, no GPU |
| Vector DB | ChromaDB | Open source, metadata filtering |
| Backend | Python | ML/AI ecosystem |
| UI | Streamlit | Rapid chatbot prototyping |
| Deploy | Streamlit Cloud + GitHub | Free hosting, CI/CD from repo |
| Secrets | Streamlit Secrets | API keys never in GitHub |

---

## Slide 12: Deployment

# Cloud Deployment

```
GitHub (code)  →  Streamlit Cloud  →  Live App
                      │
                 Secrets (API key)
                      │
                 Build KB (on first run)
```

- **Repo:** github.com/sravanthidsdt-bia/ai-training-assistant
- **Live:** aitrainingassistant.streamlit.app
- **Security:** `.env` gitignored; keys in Streamlit Secrets only

---

## Slide 13: Evaluation

# Evaluation Results

- **20 labeled test questions** across all 4 routes
- Routing accuracy measured automatically
- Gold citations and key phrases for answer validation
- Run: `python evaluate.py`

| Route | Questions |
|-------|-----------|
| general_company | 3 |
| role_specific | 4 |
| admin_policy | 10 |
| direct_llm | 3 |

---

## Slide 14: Impact

# Expected Productivity Gains

| Metric | Before | After |
|--------|--------|-------|
| Time to find policy answer | 15–30 min | < 30 seconds |
| HR tickets (informational) | High volume | Reduced 40–60% |
| Onboarding self-sufficiency | Low | High |
| Policy compliance | Variable | Consistent |

---

## Slide 15: Limitations & Future Work

# Limitations

- Synthetic data (not real org documents)
- English only; single-turn conversations
- Knowledge base rebuilt on each cloud deploy

# Future Extensions

- Conversation memory, role-aware profiles
- Live HR/wiki integrations
- Feedback loop and analytics dashboard

---

## Slide 16: Thank You

# Thank You

**AI Training Assistant for New Employees**

- Working chatbot with RAG + hybrid routing
- 13-document knowledge base, 4 routing paths
- Deployed on Streamlit Cloud
- Evaluation framework with 20 test questions

**Live Demo:** [aitrainingassistant.streamlit.app](https://aitrainingassistant.streamlit.app)

**Questions?**
