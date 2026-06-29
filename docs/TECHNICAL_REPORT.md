# Technical Report: AI Training Assistant for New Employees

**Author:** Sravanthi  
**Project:** AI Training Assistant Capstone  
**Live Demo:** [aitrainingassistant.streamlit.app](https://aitrainingassistant.streamlit.app)  
**Repository:** [github.com/sravanthidsdt-bia/ai-training-assistant](https://github.com/sravanthidsdt-bia/ai-training-assistant)

---

## 1. Problem Statement and Business Impact

### Problem

Organizations onboard new employees with internal documentation spread across wikis, policy documents, HR portals, and team-specific guides. New hires frequently:

- Spend hours searching for answers to routine questions
- Ask the same questions repeatedly to HR, managers, and colleagues
- Miss deadlines (expense submission, timesheets, access requests) due to unclear processes
- Experience slower time-to-productivity during the first 30–90 days

### Business Impact

An AI training assistant providing instant, accurate answers can:

- **Reduce onboarding time** through self-service access to policies and procedures
- **Lower HR/IT ticket volume** for repetitive informational queries
- **Improve compliance** by surfacing correct policy information consistently
- **Accelerate role ramp-up** with role-specific guidance on demand

---

## 2. System Architecture

### Overview

The system implements a **multi-agent orchestration pipeline** with four modular components coordinated by a central decision node:

```
┌─────────────────────────────────────────────────────────────┐
│                    TrainingAssistant                         │
│  ┌──────────┐  ┌─────────────┐  ┌───────────┐  ┌─────────┐ │
│  │  Router  │→ │  Decision   │→ │ Retriever │→ │Generator│ │
│  │  Agent   │  │    Node     │  │  (RAG)    │  │ Agent   │ │
│  └──────────┘  └─────────────┘  └───────────┘  └─────────┘ │
└─────────────────────────────────────────────────────────────┘
```

| Component | File | Responsibility |
|-----------|------|----------------|
| Router Agent | `src/router.py` | Classifies questions into one of four routes |
| Decision Node | `src/assistant.py` | Selects knowledge source; skips RAG for `direct_llm` |
| Retriever | `src/retriever.py` | Top-k semantic search in ChromaDB with route filtering |
| Generator Agent | `src/generator.py` | Produces final answer via Gemini REST API |

### Deployment Architecture

```
┌──────────────┐     ┌──────────────┐     ┌─────────────────────┐
│   GitHub     │────▶│  Streamlit   │────▶│  Google Gemini API  │
│  (code repo) │     │    Cloud     │     │  (gemini-3.5-flash) │
└──────────────┘     └──────┬───────┘     └─────────────────────┘
                            │
                     ┌──────▼───────┐
                     │  ChromaDB    │
                     │  (on-server) │
                     └──────────────┘
```

- **Code** is version-controlled on GitHub (no secrets committed)
- **API keys** are stored in Streamlit Cloud Secrets (not in the repository)
- **Vector database** is built at runtime via the sidebar "Build Knowledge Base" button

---

## 3. Query Routing Design

### Hybrid Routing Strategy

Routing uses a **two-tier hybrid approach** prioritizing speed and safety:

| Priority | Method | When Used |
|----------|--------|-----------|
| 1 | Keyword rules | High-confidence patterns (e.g., "data analyst", "expense", "my salary") |
| 2 | LLM classification | Ambiguous questions when keywords don't match |
| 3 | Default fallback | `admin_policy` when classification is uncertain |

**Design rationale:** Keyword rules are fast and deterministic for sensitive `direct_llm` cases (salary, leave approval). LLM classification handles nuanced questions. Sensitive requests are never sent to document retrieval.

### Route Definitions

| Route | Trigger Examples | Knowledge Paths |
|-------|-----------------|-----------------|
| `general_company` | Values, work hours, org structure, common tools | `corpus/company/` |
| `role_specific` | Job responsibilities, 30-day expectations, team workflows | `corpus/roles/` |
| `admin_policy` | Expenses, PTO, HR, IT access, timesheets, compliance | `corpus/policies/`, `corpus/admin/`, `corpus/faq/` |
| `direct_llm` | Personal data, action requests, out-of-scope topics | None (LLM only) |

### Decision Flow

```
Input Question
     │
     ├─ Keyword match for direct_llm? ──Yes──► direct_llm (refusal path)
     │
     ├─ Keyword match for other route? ──Yes──► use keyword route
     │
     ├─ LLM classification available? ──Yes──► use LLM route
     │
     └─ Default ──► admin_policy
```

---

## 4. Knowledge Sources and Retrieval (RAG)

### Knowledge Base

**13 synthetic markdown documents** organized by route (68 chunks after ingestion):

| Folder | Documents | Content |
|--------|-----------|---------|
| `corpus/company/` | company_overview.md | Mission, values, work hours, tools |
| `corpus/roles/` | data_analyst_role.md, product_manager_role.md | Role guides |
| `corpus/policies/` | expense, leave, conduct, security | Policy documents |
| `corpus/admin/` | HR, IT, timesheets, travel, onboarding | Admin processes |
| `corpus/faq/` | onboarding_faq.md | Common onboarding FAQ |

### Ingestion Pipeline

1. **Load** all `.md` files from `corpus/`
2. **Chunk** by markdown `##` sections (600 chars, 80 char overlap)
3. **Tag** metadata: `source`, `section`, `route`, `doc_name`
4. **Embed** using ChromaDB built-in ONNX MiniLM (local, no GPU required)
5. **Store** in ChromaDB with cosine similarity search

### Retrieval Strategy

- **Top-k:** 4 most relevant chunks per query
- **Route filtering:** Chunks filtered by `route` metadata before ranking
- **Context formatting:** Retrieved chunks include source document names for citation

---

## 5. LLM Integration

### Model

**Google Gemini 3.5 Flash** — selected for speed, quality, and free-tier API availability.

### API Integration

The generator uses the **Gemini REST API directly** via `httpx`, not the deprecated `google-generativeai` SDK:

- **Endpoint:** `generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent`
- **Authentication:** `x-goog-api-key` header (supports both `AIza` and newer `AQ.` auth key formats)
- **System instruction:** Defines assistant role, tone, and boundaries
- **RAG prompt:** Injects retrieved context with source labels

### Why REST API?

Newer Google **authorization keys** (`AQ.` prefix) are not supported by the legacy SDK. Direct REST calls with `x-goog-api-key` are the documented native authentication method.

### Prompt Design

| Prompt Type | Purpose |
|-------------|---------|
| System prompt | Role definition, grounding rules, refusal boundaries |
| RAG prompt | Context + question → grounded answer with citations |
| Direct LLM prompt | Refusal/redirect for personal or out-of-scope requests |
| Router prompt | Single-category classification for ambiguous questions |

### Fallback Handling

| Scenario | Behavior |
|----------|----------|
| Personal data (salary, tax) | Route to `direct_llm`; redirect to HR payroll |
| Action requests (approve leave) | Explain limitations; point to HR portal |
| Missing document context | Admit gap; suggest contacting HR/IT |
| Sensitive topics | Professional refusal with escalation path |

---

## 6. Configuration and Secrets

| Environment | API Key Location |
|-------------|-----------------|
| Local development | `.env` file (`GEMINI_API_KEY=...`) |
| Streamlit Cloud | App Settings → Secrets (TOML format) |
| GitHub | **Never** — `.env` is in `.gitignore` |

`src/env_config.py` loads keys from environment variables first, then falls back to `st.secrets` for cloud deployment.

---

## 7. Evaluation

### Test Set

**20 labeled questions** in `evaluation_set.csv` covering all four routes:

| Route | Count | Examples |
|-------|-------|---------|
| general_company | 3 | Core values, work hours, common tools |
| role_specific | 4 | DA 30-day plan, PM responsibilities |
| admin_policy | 10 | Expenses, PTO, IT access, timesheets |
| direct_llm | 3 | Salary, leave approval, performance plan |

### Metrics

- **Routing accuracy:** % of questions classified to the correct route
- **Source retrieval:** Number and relevance of chunks retrieved
- **Answer quality:** Key phrase match against gold answers

Run: `python evaluate.py`

---

## 8. Limitations

1. **Synthetic data** — Corpus is fictional; production requires real organizational documents
2. **English only** — No multilingual support
3. **Static knowledge** — Documents must be re-ingested when policies change
4. **No user authentication** — No role-based access control
5. **Single-turn chat** — No conversation memory across turns
6. **Cold start on cloud** — Knowledge base must be built after each fresh deploy
7. **API dependency** — Requires internet access for Gemini API calls

---

## 9. Future Improvements

| Area | Enhancement |
|------|------------|
| Conversation memory | Multi-turn context for follow-up questions |
| User profiles | Role-aware defaults based on employee profile |
| Live integrations | Connect to HR portal, ticketing system, wiki |
| Feedback loop | Thumbs up/down to improve retrieval and routing |
| Hybrid search | Combine vector search with BM25 keyword search |
| Pre-built vector DB | Bundle embeddings in deployment to skip cold-start ingest |
| Analytics dashboard | Track common questions and knowledge gaps |

---

## 10. Conclusion

This prototype demonstrates a practical AI training assistant using established GenAI patterns: **hybrid query routing**, **RAG over multiple knowledge sources**, **system prompting**, **graceful fallback** for out-of-scope requests, and **cloud deployment** with secure secrets management. The modular architecture separates routing, retrieval, and generation, making it straightforward to extend with additional knowledge sources, routes, or LLM providers.
