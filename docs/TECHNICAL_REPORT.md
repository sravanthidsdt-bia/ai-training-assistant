# Technical Report: AI Training Assistant for New Employees

## 1. Problem Statement and Business Impact

### Problem

Organizations onboard new employees with a large volume of internal documentation spread across wikis, policy PDFs, HR portals, and team-specific guides. New hires frequently:

- Spend hours searching for answers to routine questions
- Ask the same questions repeatedly to HR, managers, and colleagues
- Miss important deadlines (expense submission, timesheets, access requests) due to unclear processes
- Experience slower time-to-productivity during the first 30–90 days

### Business Impact

An AI training assistant that provides instant, accurate answers can:

- **Reduce onboarding time** by giving self-service access to policies and procedures
- **Lower HR/IT ticket volume** for repetitive informational queries
- **Improve compliance** by surfacing correct policy information consistently
- **Accelerate role ramp-up** with role-specific guidance on demand

This capstone builds a working prototype demonstrating these capabilities using RAG, query routing, and LLM generation.

---

## 2. Architecture and Routing Design

### System Architecture

The system follows a **multi-agent orchestration pipeline** with four specialized components:

1. **Router Agent** (`src/router.py`) — Classifies incoming questions into one of four routes
2. **Decision Node** (`src/assistant.py`) — Selects the knowledge source path based on classification
3. **Retriever** (`src/retriever.py`) — Fetches top-k relevant document chunks from ChromaDB
4. **Generator Agent** (`src/generator.py`) — Produces the final answer using Google Gemini

### Routing Logic

Routing uses a **hybrid approach** combining keyword rules and LLM classification:

| Priority | Method | When Used |
|----------|--------|-----------|
| 1 | Keyword rules | High-confidence patterns (e.g., "my salary", "data analyst") |
| 2 | LLM classification | Gemini classifies ambiguous questions |
| 3 | Default fallback | `admin_policy` when no strong signal |

#### Route Definitions

| Route | Trigger Examples | Knowledge Paths |
|-------|-----------------|-----------------|
| `general_company` | Values, work hours, org structure, common tools | `corpus/company/` |
| `role_specific` | Job responsibilities, 30-day expectations, team workflows | `corpus/roles/` |
| `admin_policy` | Expenses, PTO, HR, IT access, timesheets, compliance | `corpus/policies/`, `corpus/admin/`, `corpus/faq/` |
| `direct_llm` | Personal data, action requests, out-of-scope topics | None (LLM only) |

#### Decision Flow

```
Input Question
     │
     ├─ Keyword match for direct_llm? ──Yes──► direct_llm path
     │
     ├─ LLM classification available? ──Yes──► use LLM route
     │
     ├─ Keyword match for other routes? ──Yes──► use keyword route
     │
     └─ Default ──► admin_policy
```

### Why Hybrid Routing?

- **Keyword rules** are fast, deterministic, and reliable for sensitive `direct_llm` cases (salary, leave approval)
- **LLM classification** handles nuanced questions that keywords miss (e.g., "What should I focus on in my first month as a PM?")
- **Default fallback** ensures every question gets a response even when classification is uncertain

---

## 3. Knowledge Sources and Retrieval Approach

### Knowledge Base Structure

The corpus contains **13 synthetic markdown documents** organized by route:

| Folder | Documents | Content |
|--------|-----------|---------|
| `corpus/company/` | company_overview.md | Mission, values, work hours, tools |
| `corpus/roles/` | data_analyst_role.md, product_manager_role.md | Role guides and expectations |
| `corpus/policies/` | expense, leave, conduct, security | Policy documents |
| `corpus/admin/` | HR, IT, timesheets, travel, onboarding | Administrative processes |
| `corpus/faq/` | onboarding_faq.md | Common onboarding questions |

### Ingestion Pipeline

1. **Load** all `.md` files from `corpus/`
2. **Chunk** by markdown sections (`##` headers) with 600-char chunks and 80-char overlap
3. **Tag** each chunk with metadata: `source`, `section`, `route`, `doc_name`
4. **Embed** using ChromaDB's built-in ONNX MiniLM model (local, no torch)
5. **Store** in ChromaDB with cosine similarity search

### Retrieval Strategy

- **Top-k retrieval**: 4 most relevant chunks per query
- **Route filtering**: Chunks are filtered by `route` metadata before ranking
- **Context formatting**: Retrieved chunks are formatted with source citations for the LLM

### Vector Database

**ChromaDB** was chosen because it is:
- Open source and free
- Runs locally with no external service dependency
- Supports metadata filtering (critical for route-based retrieval)
- Persistent across application restarts

---

## 4. Prompt Design and Fallback Handling

### System Prompt

The system prompt defines the assistant's role, tone, and boundaries:
- Professional and concise onboarding helper
- Ground answers in provided context only
- Refuse personal data requests
- Suggest appropriate contacts when information is unavailable

### RAG Prompt Template

For routed questions, the generator receives:
- Retrieved document context with source labels
- The employee's question
- Instructions to cite policy names and admit when context is insufficient

### Direct LLM Fallback Prompt

For `direct_llm` route, a specialized prompt instructs the model to:
- **Not** invent personal information
- **Not** pretend to approve requests
- Politely redirect to HR portal, manager, or IT
- Provide generic templates when appropriate (e.g., performance plan structure)

### Handling Ambiguity

| Scenario | Behavior |
|----------|----------|
| Question matches no documents | LLM states it lacks information; suggests HR/IT contact |
| Personal/sensitive request | Routed to `direct_llm`; refusal with redirect |
| Action request (approve leave) | Routed to `direct_llm`; explains it cannot take actions |
| Multi-topic question | Retrieves from primary route; LLM synthesizes across chunks |

---

## 5. Evaluation

A labeled evaluation set of **20 questions** (`evaluation_set.csv`) covers all four routes:

| Route | Questions | Examples |
|-------|-----------|---------|
| general_company | 3 | Core values, work hours, common tools |
| role_specific | 4 | DA 30-day plan, PM responsibilities |
| admin_policy | 10 | Expenses, PTO, IT access, timesheets |
| direct_llm | 3 | Salary, leave approval, performance plan |

Run evaluation with:

```bash
python evaluate.py
```

Metrics reported:
- **Routing accuracy**: % of questions classified to the correct route
- **Source retrieval**: Number of chunks retrieved per question
- **Answer preview**: First 120 characters of generated answer

---

## 6. Limitations

1. **Synthetic data only** — Corpus is fictional; real deployment requires actual organizational documents
2. **English only** — No multilingual support
3. **Static knowledge** — Documents must be re-ingested when policies change
4. **No authentication** — No user identity or role-based access control
5. **Single-turn chat** — No conversation memory across turns
6. **Embedding model size** — `all-MiniLM-L6-v2` is fast but less accurate than larger models
7. **API dependency** — Requires internet access for Gemini API calls
8. **No action execution** — Cannot submit tickets, approve requests, or access live systems

---

## 7. Future Improvements

| Area | Enhancement |
|------|------------|
| **Conversation memory** | Multi-turn context for follow-up questions |
| **User profiles** | Role-aware defaults (auto-detect employee role) |
| **Live integrations** | Connect to HR portal, ticketing system, wiki |
| **Feedback loop** | Thumbs up/down to improve retrieval and routing |
| **Larger embeddings** | Upgrade to `bge-large` or OpenAI embeddings |
| **Hybrid search** | Combine vector search with BM25 keyword search |
| **Guardrails** | PII detection, content filtering, audit logging |
| **Analytics dashboard** | Track common questions, routing accuracy, gaps |
| **Multi-language** | Support for global workforces |
| **Automated ingestion** | Watch document folders and auto-reindex on changes |

---

## 8. Conclusion

This prototype demonstrates a practical AI training assistant using established GenAI patterns: **query routing**, **RAG over multiple knowledge sources**, **system prompting**, and **graceful fallback** for out-of-scope requests. The modular architecture separates routing, retrieval, and generation concerns, making it straightforward to extend with additional knowledge sources, routes, or LLM providers.
