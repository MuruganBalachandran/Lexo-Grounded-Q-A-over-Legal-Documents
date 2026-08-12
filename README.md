# Legixo Gen AI Intern Take-Home — Document Q&A API

A document-grounded Q&A HTTP API built with **Python**, **LangGraph**, **Gemini**, and **Pinecone**.  
Answers questions **strictly from a fictional legal document corpus** — with source citations.  
If the documents don't say it, the system honestly refuses rather than hallucinating.

---

🎥 **[Watch the 5-Minute Architecture & Demo Walkthrough](https://drive.google.com/file/d/1fr8LRYbvvHZGsMt9jrsmFqDhPzsR6XO8/view?usp=sharing)**

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Full-Stack Setup Guide](#full-stack-setup-guide)
4. [API Reference & cURL Examples](#api-reference--curl-examples)
5. [LangGraph Flow](#langgraph-flow)
6. [Evaluation & Self-test](#evaluation--self-test)
7. [Pinecone Details](#pinecone-details)
8. [Project Structure](#project-structure)
9. [AI Tools Used](#ai-tools-used)
10. [Demo Video](#demo-video)

---

## Architecture Overview

```text
Client
  │  POST /ask  {"question": "..."}
  ▼
FastAPI (backend/main.py)
  │
  ▼
LangGraph StateGraph (backend/pipeline/graph/)
  │
  ├─ retrieve      → Pinecone vector search (Gemini gemini-embedding-001)
  ├─ grade_chunks  → Gemini 2.5 Flash LLM relevance judge
  ├─ generate      → Grounded answer + citations  (good path)
  └─ not_found     → Honest refusal               (bad path)
```

Key choices:
- **Section-level chunking** (split on `##` markdown headers) — keeps related legal facts together in one chunk, directly matching the gold-set questions.
- **Asymmetric embeddings** — `RETRIEVAL_DOCUMENT` at ingest, `RETRIEVAL_QUERY` at query time.
- **LLM-as-judge** grading catches near-miss retrievals (e.g., out-of-corpus questions that look similar to in-corpus facts).
- **Loop guard** — at most `MAX_RETRIES=2` retrieval attempts; cannot spin forever.
- **REST API calls** — embeddings and chat both call the Gemini v1 REST API directly via `requests`, avoiding SDK version issues.

---

## Prerequisites

| Tool | Version |
|------|---------|
| Python | 3.10 or newer |
| Node.js| 18+ (for frontend UI) |
| Git | any |

You need API keys for:
- [Google AI Studio](https://aistudio.google.com/) — for Gemini Flash + text-embedding-004 (free tier works)
- [Pinecone](https://app.pinecone.io/) — free Starter plan is enough

---

## Full-Stack Setup Guide

### 1. Environment Variables (Backend)

First, configure your API keys.

```bash
cd backend
cp .env.example .env
```

Open `.env` and configure:

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Google AI Studio API key | Yes |
| `PINECONE_API_KEY` | Pinecone API key | Yes |
| `PINECONE_INDEX_NAME` | Name of the index (default: `legixo-qa`) | Yes |
| `PINECONE_CLOUD` | Serverless cloud provider (default: `aws`) | optional |
| `PINECONE_REGION` | Serverless region (default: `us-east-1`) | optional |

> **Note:** Never commit `.env` to git. It is already listed in `.gitignore`.

### 2. Start the Backend API

```bash
cd backend
python -m venv .venv

# Activate Virtual Environment
.venv\Scripts\activate     # Windows
source .venv/bin/activate  # macOS / Linux

# Install dependencies
pip install -r requirements.txt

# Ingest the fictional corpus into Pinecone
python -m pipeline.ingest

# Run the API Server (starts on port 8000)
python -m uvicorn main:app --reload
```

### 3. Start the Frontend UI (Optional but Recommended)

```bash
cd frontend

# Install Node dependencies
npm install

# Start the Vite development server (starts on port 5173)
npm run dev
```
Open **[http://localhost:5173](http://localhost:5173)** to query the Q&A system using the "Ledger" interface!

---

## API Reference & cURL Examples

If you prefer testing the backend without the frontend, you can use the interactive Swagger UI at **[http://localhost:8000/docs](http://localhost:8000/docs)**, or use `curl`:

**Health Check:**
```bash
curl http://localhost:8000/
```

**Ask an In-Corpus Question:**
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What notice period applies when Bluecrest ends the employment agreement?"}'
```

**Ask an Out-of-Corpus Question (Refusal Test):**
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Who won case CV-2024-8812?"}'
```

---

## LangGraph Flow

A short summary of the LangGraph node logic is available in:
**[`backend/langgraph.md`](backend/langgraph.md)** (includes the full node description table and Mermaid diagram).

**Quick flow:**
```text
START → retrieve → grade_chunks → [conditional edge]
                                    ├─ sufficient   → generate → END
                                    ├─ insufficient + retries left → retrieve (loop)
                                    └─ insufficient + no retries   → not_found → END
```

---

## Evaluation & Self-test

The project includes an evaluation suite that tests against the provided gold-set (`sample_test_cases.json`).

```bash
cd backend
python eval/run_eval.py
```

The script runs all 19 test cases (16 in-corpus + 3 out-of-corpus) and saves a detailed report to `eval/results.md`.

---

## Pinecone Details

**Creation:** The index is **created automatically** the first time you run ingest (if it doesn't already exist). It automatically configures it with 3072 dimensions for the Gemini model and cosine metric. No manual console steps are needed.

**Running Ingest Twice:** It is safe to run ingest multiple times. Chunk IDs are deterministic (`source_file::section_slug`). Pinecone `upsert` with existing IDs simply overwrites the vector rather than creating duplicates.

---

## Project Structure

```text
legixo-assignment/
├── backend/               # Python FastAPI backend (see backend/README.md)
│   ├── core/              # Config and Pydantic settings
│   ├── pipeline/          # LangGraph QA flow, embeddings, and Pinecone client
│   ├── eval/              # Test cases and evaluation scripts
│   └── corpus/            # Fictional legal .md files
├── frontend/              # React + Vite frontend (see frontend/README.md)
│   ├── src/               # React application source code
│   └── tailwind.config.js # Tailwind CSS configuration
├── .gitignore
└── README.md
```

---

## AI Tools Used

I used AI tools to accelerate the development of this project. Specifically:
- **Antigravity (Gemini Pro, Claude Sonnet)**: Served as an AI engineering assistant to help automate boilerplate code, rapidly refactor the UI into Tailwind CSS, and execute terminal commands during setup.
- **Claude AI**: Helped brainstorm the high-level architecture, state management patterns, and design system choices (like the "Ledger" theme).

---

## Demo Video

**[Watch the 5-minute walkthrough](https://drive.google.com/file/d/1fr8LRYbvvHZGsMt9jrsmFqDhPzsR6XO8/view?usp=sharing)**

Covers:
1. Install & env setup
2. Ingest corpus (`python -m pipeline.ingest`)
3. Start server (`uvicorn main:app --reload`)
4. Ask endpoint demo (both in-corpus citations and out-of-corpus refusals)
5. LangGraph diagram walkthrough
