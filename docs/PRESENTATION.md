# AI Training Assistant — Presentation Deck

> Use this document as slide content. Each `---` separator represents a new slide.

---

## Slide 1: Title

# AI Training Assistant for New Employees

**Capstone Project**

An intelligent onboarding assistant that routes questions to the right knowledge sources and generates context-aware answers.

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
3. **Retrieves** relevant policy and role documents
4. **Generates** clear, grounded answers

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
                    Google Gemini
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

**Hybrid routing:** Keyword rules + LLM classification

---

## Slide 6: Knowledge Sources

# Multi-Source Knowledge Base

**13 synthetic documents** across 5 categories:

- **Company** — Mission, values, work model
- **Roles** — Data Analyst, Product Manager guides
- **Policies** — Expense, leave, conduct, security
- **Admin** — HR processes, IT access, timesheets, travel
- **FAQ** — Common onboarding questions

Stored in **ChromaDB** with semantic embeddings for fast retrieval.

---

## Slide 7: RAG Pipeline

# Retrieval-Augmented Generation

1. **Chunk** documents by section (600 chars, 80 overlap)
2. **Embed** with ChromaDB built-in ONNX MiniLM (local, free)
3. **Store** in ChromaDB with route metadata
4. **Retrieve** top-4 relevant chunks per query
5. **Generate** answer with Gemini using retrieved context

> Answers are **grounded in real documents**, not hallucinated.

---

## Slide 8: Demo Scenarios

# Live Demo Scenarios

| # | Question | Expected Route |
|---|----------|---------------|
| 1 | "What are the company's core values?" | General Company |
| 2 | "First 30 days as a Data Analyst?" | Role-Specific |
| 3 | "How do I submit an expense claim?" | Admin / Policy |
| 4 | "What is my exact salary breakup?" | Direct LLM (refusal) |

Each answer shows the **route badge** and **source citations**.

---

## Slide 9: Fallback Handling

# Graceful Fallbacks

When the assistant **cannot** answer from documents:

- **Personal data** (salary, tax) → Redirect to HR payroll
- **Action requests** (approve leave) → Explain limitations; point to portal
- **Missing information** → Admit gap; suggest contacting the right team
- **Sensitive topics** → Professional refusal with escalation path

No hallucinated policies. No fake approvals.

---

## Slide 10: Tech Stack

# Technology Choices

| Layer | Technology | Why |
|-------|-----------|-----|
| LLM | Google Gemini 3.5 Flash | Free API tier, fast, capable |
| Embeddings | ChromaDB ONNX MiniLM | Local, no API cost, no torch |
| Vector DB | ChromaDB | Open source, metadata filtering |
| Backend | Python | Ecosystem for ML/AI |
| UI | Streamlit | Rapid chatbot prototyping |
| Orchestration | Custom pipeline | Full control over routing logic |

---

## Slide 11: Impact & Productivity Gains

# Expected Impact

| Metric | Before | After |
|--------|--------|-------|
| Time to find policy answer | 15–30 min | < 30 seconds |
| HR tickets (informational) | High volume | Reduced 40–60% |
| Onboarding self-sufficiency | Low | High |
| Policy compliance | Variable | Consistent |
| Manager interruptions | Frequent | Decreased |

*Estimates based on industry onboarding benchmarks.*

---

## Slide 12: Evaluation

# Evaluation Results

- **20 labeled test questions** across all 4 routes
- Routing accuracy measured automatically
- Gold citations and key phrases for answer validation
- Run: `python evaluate.py`

Covers: company info, role guides, policies, and fallback scenarios.

---

## Slide 13: Limitations

# Current Limitations

- Synthetic data (not real org documents)
- English only
- No user authentication or role profiles
- Single-turn conversations (no memory)
- Requires internet for Gemini API
- Static knowledge (manual re-ingestion needed)

---

## Slide 14: Future Extensions

# Potential Extensions

- **Conversation memory** for follow-up questions
- **Role-aware defaults** based on employee profile
- **Live integrations** with HR portal and ticketing
- **Feedback loop** to improve over time
- **Analytics dashboard** for common question trends
- **Multi-language support** for global teams
- **Automated document ingestion** on policy updates

---

## Slide 15: Thank You

# Thank You

**AI Training Assistant for New Employees**

- Working chatbot prototype with RAG + routing
- 13-document knowledge base across 4 routes
- Evaluation framework with 20 test questions
- Full documentation and reproducible setup

**Questions?**

```bash
streamlit run app.py
```
