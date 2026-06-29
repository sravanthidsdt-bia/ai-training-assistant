# AI Training Assistant — Jury Writeup

**Project Title:** AI Training Assistant for New Employees  
**Author:** Sravanthi  
**Live Demo:** [https://aitrainingassistant.streamlit.app](https://aitrainingassistant.streamlit.app)  
**Source Code:** [https://github.com/sravanthidsdt-bia/ai-training-assistant](https://github.com/sravanthidsdt-bia/ai-training-assistant)

---

## 1. What Is This Project?

This is an **AI-powered chatbot** that helps new employees get answers about company policies, their job role, HR processes, and onboarding steps — instantly, without searching through multiple documents or waiting for a colleague.

You type a question in plain English, and the assistant:
1. Figures out **what type of question** it is
2. Looks up the **right internal documents**
3. Generates a **clear, accurate answer** with source citations

---

## 2. Why Does This Matter?

When a new employee joins a company, they face questions like:

- "What are the company's core values?"
- "How do I submit an expense claim?"
- "What should I focus on in my first 30 days as a Data Analyst?"
- "How do I request PTO?"

Today, finding these answers means searching wikis, reading PDFs, or asking HR/managers. This project automates that process using **Artificial Intelligence**.

**Business value:**
- Faster onboarding (answers in seconds, not hours)
- Less burden on HR and senior staff
- Consistent, policy-compliant answers every time

---

## 3. How Does It Work? (End-to-End Flow)

Here is exactly what happens when an employee asks a question:

### Step 1: Employee Asks a Question

The employee types a question in the Streamlit chat interface, for example:
> *"How do I submit an expense claim?"*

### Step 2: Router Agent Classifies the Question

The **Router Agent** (`src/router.py`) decides which category the question belongs to:

| Category | What It Covers |
|----------|---------------|
| **General Company** | Values, work hours, org structure |
| **Role-Specific** | Job duties, team expectations |
| **Admin / Policy** | Expenses, PTO, HR, IT, timesheets |
| **Direct LLM** | Personal data, action requests (salary, approve leave) |

**How routing works:** The system uses **keyword rules first** (fast and safe — e.g., "salary" always goes to Direct LLM), then **LLM classification** for ambiguous questions.

For our example, *"expense claim"* matches keywords → route = **Admin / Policy**.

### Step 3: Decision Node Selects Knowledge Source

The **Decision Node** (`src/assistant.py`) picks the right knowledge base:

- Admin/Policy questions → search `corpus/policies/`, `corpus/admin/`, `corpus/faq/`
- Role questions → search `corpus/roles/`
- General questions → search `corpus/company/`
- Direct LLM → **no document search** (goes straight to the LLM)

### Step 4: Retriever Finds Relevant Documents (RAG)

For Admin/Policy route, the **Retriever** (`src/retriever.py`):

1. Converts the question into a **vector embedding** (numerical representation)
2. Searches **ChromaDB** (vector database) for the 4 most similar document chunks
3. Filters results to only Admin/Policy documents
4. Returns chunks like:

   > *[Source: expense_policy.md — Submission Process]*  
   > *"Submit within 10 days of incurring the expense. Attach itemized receipt..."*

This is **Retrieval-Augmented Generation (RAG)** — the LLM gets real documents as context instead of guessing.

### Step 5: Generator Produces the Answer

The **Generator Agent** (`src/generator.py`):

1. Sends the retrieved documents + the employee's question to **Google Gemini 3.5 Flash**
2. Uses a **system prompt** that says: "Only answer from the provided context. Cite sources. Don't make things up."
3. Returns a clear answer, for example:

   > *"To submit an expense claim, use the expense portal and submit within 10 days of incurring the expense. Attach an itemized receipt and choose the correct cost center. Manager approval is required for amounts above 2,000. (Source: expense_policy.md)"*

### Step 6: UI Shows Answer with Metadata

The Streamlit UI displays:
- The answer text
- A **route badge** (e.g., "Administrative / Policy · keyword")
- **Source citations** (document name, section, relevance score)

---

## 4. What About Questions It Can't Answer?

For sensitive or personal questions like *"What is my salary?"*:

1. Router sends it to **Direct LLM** path (no document retrieval)
2. A special **refusal prompt** tells Gemini to:
   - NOT invent personal information
   - NOT pretend to approve requests
   - Politely redirect to HR portal or manager

Example response:
> *"I don't have access to personal payroll information. Please contact HR through the employee portal or reach out to your HR business partner for salary details."*

---

## 5. Key Technologies Used

| What | Technology | Why I Chose It |
|------|-----------|----------------|
| **Large Language Model** | Google Gemini 3.5 Flash | Free API, fast, high quality |
| **API Method** | REST API with httpx | Supports new Google auth keys (`AQ.` format) |
| **Vector Database** | ChromaDB | Free, local, supports metadata filtering by route |
| **Embeddings** | ChromaDB ONNX MiniLM | No GPU needed, runs on any machine |
| **Backend** | Python 3.10+ | Standard for AI/ML projects |
| **User Interface** | Streamlit | Quick to build a professional chatbot |
| **Hosting** | Streamlit Cloud | Free deployment from GitHub |
| **Version Control** | GitHub | Code sharing and CI/CD |

---

## 6. Knowledge Base Details

I created **13 synthetic (fictional) documents** simulating a real company's internal docs:

| Folder | Files | Content |
|--------|-------|---------|
| `corpus/company/` | 1 file | Company overview, values, work hours |
| `corpus/roles/` | 2 files | Data Analyst and Product Manager guides |
| `corpus/policies/` | 4 files | Expense, leave, conduct, security policies |
| `corpus/admin/` | 5 files | HR, IT access, timesheets, travel, onboarding |
| `corpus/faq/` | 1 file | Common onboarding FAQ |

These are chunked into **68 pieces**, embedded, and stored in ChromaDB for fast semantic search.

---

## 7. GenAI Concepts Demonstrated

This project applies the following **Generative AI concepts** from the course:

| Concept | How It's Used |
|---------|--------------|
| **Large Language Models (LLMs)** | Gemini 3.5 Flash generates all answers |
| **System Prompting** | Defines assistant role, tone, and safety boundaries |
| **Retrieval-Augmented Generation (RAG)** | Retrieves real docs before generating answers |
| **Query Classification & Routing** | Routes questions to the correct knowledge source |
| **Multi-Source Knowledge Integration** | 4 separate knowledge bases by category |
| **Fallback Handling** | Graceful refusal for personal/out-of-scope requests |
| **Vector Embeddings & Semantic Search** | ChromaDB finds relevant chunks by meaning |
| **Agent-Style Orchestration** | Router → Decision → Retriever → Generator pipeline |

---

## 8. How to Run the Project

### Locally

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
# Add GEMINI_API_KEY to .env file
python -m src.ingest          # Build knowledge base
.\run.bat                     # Start chatbot
```

### On the Cloud (Already Deployed)

Visit: [https://aitrainingassistant.streamlit.app](https://aitrainingassistant.streamlit.app)

1. Click **Build Knowledge Base** in the sidebar (first time)
2. Ask any onboarding question

---

## 9. Evaluation

I created a **test set of 20 labeled questions** (`evaluation_set.csv`) covering all four routes:

- 3 general company questions
- 4 role-specific questions
- 10 admin/policy questions
- 3 direct LLM (refusal) questions

Running `python evaluate.py` measures **routing accuracy** — whether the system classifies each question into the correct category.

---

## 10. Demo Script for Jury

If you want to demonstrate live, ask these four questions in order:

| # | Question | Expected Behavior |
|---|----------|-------------------|
| 1 | "What are the company's core values?" | Answers with values list; route = General Company; cites company_overview.md |
| 2 | "As a Data Analyst, what are the first 30 days expectations?" | Answers with deliverables; route = Role-Specific; cites data_analyst_role.md |
| 3 | "How do I submit an expense claim?" | Answers with 10-day deadline; route = Admin/Policy; cites expense_policy.md |
| 4 | "What is my exact salary breakup?" | Politely refuses; route = Direct LLM; redirects to HR |

Point out the **route badge** and **source citations** in the UI for each answer.

---

## 11. Security and Deployment Notes

- **API keys are NEVER stored in GitHub** — `.env` is in `.gitignore`
- On Streamlit Cloud, the key is in **Streamlit Secrets** (encrypted, server-side only)
- All corpus documents are **synthetic/fictional** — no real company data
- The assistant **cannot take actions** (approve leave, access payroll) — it only provides information

---

## 12. Limitations and Future Scope

**Current limitations:**
- Synthetic data only (not connected to real company systems)
- English language only
- Single-turn conversations (no memory of prior messages)
- Knowledge base must be rebuilt after each cloud redeploy

**Future improvements:**
- Multi-turn conversation memory
- Role-aware defaults (auto-detect employee's role)
- Integration with live HR portal and ticketing systems
- User feedback loop (thumbs up/down)
- Analytics dashboard for common question trends

---

## 13. Summary

This project builds a **working AI training assistant** that demonstrates practical application of Generative AI for employee onboarding. It combines **query routing**, **retrieval-augmented generation**, **system prompting**, and **graceful fallback handling** in a modular, deployable system.

The assistant is **live and accessible** at [aitrainingassistant.streamlit.app](https://aitrainingassistant.streamlit.app), with full source code on [GitHub](https://github.com/sravanthidsdt-bia/ai-training-assistant).

---

*End of Jury Writeup*
