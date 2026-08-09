# Legixo Gen AI Intern Take-Home — Document Q&A API

A document-grounded Q&A HTTP API built with **Python**, **LangGraph**, **Gemini**, and **Pinecone**.  
Answers questions **strictly from a fictional legal document corpus** — with source citations.  
If the documents don't say it, the system honestly refuses rather than hallucinating.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Environment Variables](#environment-variables)
5. [Pinecone Index Setup](#pinecone-index-setup)
6. [Ingest the Corpus](#ingest-the-corpus)
7. [Run the API Server](#run-the-api-server)
8. [API Reference](#api-reference)
9. [Example curl Calls](#example-curl-calls)
10. [LangGraph Flow](#langgraph-flow)
11. [Eval / Self-test](#eval--self-test)
12. [Running Ingest Twice](#running-ingest-twice)
13. [Project Structure](#project-structure)
14. [Demo Video](#demo-video)

---

## Architecture Overview

```
Client
  │  POST /ask  {"question": "..."}
  ▼
FastAPI (app/main.py)
  │
  ▼
LangGraph StateGraph (app/graph/)
  │
  ├─ retrieve      → Pinecone vector search (Gemini text-embedding-004)
  ├─ grade_chunks  → Gemini Flash LLM relevance judge
  ├─ generate      → Grounded answer + citations  (good path)
  └─ not_found     → Honest refusal               (bad path)
```

Key choices:
- **Section-level chunking** (split on `##` markdown headers) — keeps related legal facts together in one chunk, directly matching the gold-set questions.
- **Asymmetric embeddings** — `RETRIEVAL_DOCUMENT` at ingest, `RETRIEVAL_QUERY` at query time (Gemini best practice for text-embedding-004).
- **LLM-as-judge** grading catches near-miss retrievals (e.g., out-of-corpus questions that look similar to in-corpus facts).
- **Loop guard** — at most `MAX_RETRIES=2` retrieval attempts; cannot spin forever.

---

## Prerequisites

| Tool | Version |
|------|---------|
| Python | 3.10 or newer |
| pip | latest |
| Git | any |

You need API keys for:
- [Google AI Studio](https://aistudio.google.com/) — for Gemini Flash + text-embedding-004 (free tier works)
- [Pinecone](https://app.pinecone.io/) — free Starter plan is enough

---

## Installation

```bash
# 1. Clone the repo
git clone <your-repo-url>
cd legixo-assignment

# 2. Create and activate a virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

## Environment Variables

Copy `.env.example` to `.env` and fill in your real keys:

```bash
cp .env.example .env   # macOS/Linux
copy .env.example .env # Windows
```

Open `.env` and set:

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Google AI Studio API key | ✅ |
| `PINECONE_API_KEY` | Pinecone API key | ✅ |
| `PINECONE_INDEX_NAME` | Name of the index (default: `legixo-qa`) | ✅ |
| `PINECONE_CLOUD` | Serverless cloud provider (default: `aws`) | optional |
| `PINECONE_REGION` | Serverless region (default: `us-east-1`) | optional |
| `EMBED_MODEL` | Gemini embedding model (default: `models/text-embedding-004`) | optional |
| `CHAT_MODEL` | Gemini chat model (default: `gemini-1.5-flash`) | optional |
| `TOP_K` | Pinecone top-k retrieval (default: `5`) | optional |
| `MAX_RETRIES` | LangGraph retry limit (default: `2`) | optional |
| `CORPUS_DIR` | Path to corpus folder (default: `gen_ai_takehome_sample_corpus`) | optional |

> ⚠️ **Never commit `.env` to git** — it is listed in `.gitignore`.

---

## Pinecone Index Setup

The index is **created automatically** the first time you run ingest (if it doesn't already exist).

**What gets created:**
- Name: value of `PINECONE_INDEX_NAME` (default `legixo-qa`)
- Type: Serverless (free tier)
- Dimension: **768** (Gemini `text-embedding-004` output size)
- Metric: cosine

**Required env vars for index creation:**
```
PINECONE_API_KEY=...
PINECONE_INDEX_NAME=legixo-qa
PINECONE_CLOUD=aws
PINECONE_REGION=us-east-1
```

No manual Pinecone console steps needed.

---

## Ingest the Corpus

### Option A — CLI (recommended)

```bash
python -m app.ingest
```

With a custom corpus directory:
```bash
python -m app.ingest --dir path/to/your/corpus
```

### Option B — API route (after starting the server)

```bash
curl -X POST http://localhost:8000/ingest
```

**What ingest does:**
1. Creates the Pinecone index if it doesn't exist.
2. Reads all `.md` files from `gen_ai_takehome_sample_corpus/`.
3. Splits each file by `##` section headings (one chunk per section).
4. Embeds each chunk with Gemini `text-embedding-004` (`RETRIEVAL_DOCUMENT` task).
5. Upserts vectors to Pinecone with metadata: `chunk_id`, `source_file`, `section_title`, `text`.

Expected output:
```
[ingest] Starting ingest from 'gen_ai_takehome_sample_corpus' ...
[pinecone] Index 'legixo-qa' already exists — skipping creation.
  [chunker] 01_matter_memo_arvind_v_northfield.md → 3 chunk(s)
  [chunker] 02_employment_agreement_excerpt.md → 4 chunk(s)
  ...
[ingest] Done. 18 vectors upserted from 6 file(s).
```

---

## Run the API Server

```bash
uvicorn app.main:app --reload
```

The server starts at **http://localhost:8000**.

Interactive API docs (OpenAPI / Swagger UI):
```
http://localhost:8000/docs
```

---

## API Reference

### `GET /`
Health check.

**Response:**
```json
{ "status": "ok", "service": "legixo-qa-api", "version": "1.0.0" }
```

---

### `POST /ask`
Answer a question from the document corpus.

**Request:**
```json
{ "question": "string (3–2000 chars)" }
```

**Response:**
```json
{
  "answer": "string",
  "citations": [
    {
      "source_file": "02_employment_agreement_excerpt.md",
      "chunk_id": "02_employment_agreement_excerpt.md::notice_period",
      "snippet": "Either party may end this agreement by giving 60 days written notice...",
      "score": 0.9123
    }
  ],
  "grounded": true,
  "trace": ["retrieve", "grade_chunks", "generate"]
}
```

| Field | Description |
|-------|-------------|
| `answer` | Grounded answer or honest refusal |
| `citations` | Source chunks used (empty on refusal) |
| `grounded` | `true` = answered from corpus; `false` = refused |
| `trace` | LangGraph nodes visited (for observability) |

---

### `POST /ingest`
Trigger corpus ingest from the API.

**Response:**
```json
{ "files_processed": 6, "chunks_upserted": 18, "message": "Ingest complete." }
```

---

## Example curl Calls

### Health check
```bash
curl http://localhost:8000/
```

### Ask a question (in-corpus)
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What notice period applies when Bluecrest ends the employment agreement?"}'
```

### Ask a question (out-of-corpus — should be refused)
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Who won case CV-2024-8812?"}'
```

### Trigger ingest via API
```bash
curl -X POST http://localhost:8000/ingest
```

### Windows PowerShell equivalent
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/ask" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"question": "What is the monthly rent for Unit 4B?"}'
```

---

## LangGraph Flow

See **[docs/langgraph.md](docs/langgraph.md)** for the full node description table and Mermaid diagram.

**Quick summary:**

```
START → retrieve → grade_chunks → [conditional edge]
                                    ├─ sufficient   → generate → END
                                    ├─ insufficient + retries left → retrieve (loop)
                                    └─ insufficient + no retries   → not_found → END
```

- **retrieve**: vector search Pinecone top-k
- **grade_chunks**: Gemini LLM judges if chunks actually answer the question
- **generate**: grounded answer + citations (good path)
- **not_found**: honest refusal, no fabrication (bad path)
- Loop cap: `MAX_RETRIES=2` — at most 3 total retrieval attempts

---

## Eval / Self-test

```bash
# Server must be running
python eval/run_eval.py

# Custom host
python eval/run_eval.py --host http://localhost:8000
```

The script runs all 19 test cases (16 in-corpus + 3 out-of-corpus) and saves a detailed report to `eval/results.md`.

Checks:
- **In-corpus**: answer contains expected facts (substring) + citations include expected source file
- **Out-of-corpus**: response is a refusal (`grounded=False` or refusal phrasing)

---

## Running Ingest Twice

**It is safe.** Chunk IDs are deterministic:

```
chunk_id = f"{source_file}::{section_slug}"
# e.g. "02_employment_agreement_excerpt.md::notice_period"
```

Pinecone `upsert` with existing IDs **overwrites** the vector — it does not create duplicates. The vector count remains the same after a second ingest run.

---

## Project Structure

```
legixo-assignment/
├── app/
│   ├── config.py          # Pydantic settings (reads .env)
│   ├── embeddings.py      # Gemini text-embedding-004 wrapper
│   ├── pinecone_client.py # Index creation + connection
│   ├── chunker.py         # Section-based markdown splitter
│   ├── ingest.py          # Ingest pipeline (CLI + function)
│   ├── models.py          # FastAPI Pydantic schemas
│   ├── main.py            # FastAPI app (/ask, /ingest, /health)
│   └── graph/
│       ├── state.py       # QAState TypedDict
│       ├── nodes.py       # retrieve, grade_chunks, generate, not_found
│       └── graph.py       # StateGraph wiring + compilation
├── docs/
│   └── langgraph.md       # Node table + Mermaid diagram
├── eval/
│   ├── test_cases.json    # 19 Q&A test cases
│   ├── run_eval.py        # Automated eval script
│   └── results.md         # Generated after running eval
├── gen_ai_takehome_sample_corpus/   # 6 fictional legal .md files
├── .env.example           # Dummy env vars template
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Demo Video

🎬 **[Watch the 5-minute walkthrough](#)**  
*(Link will be added before submission)*

Covers:
1. Install & env setup
2. Ingest corpus (`python -m app.ingest`)
3. Start server (`uvicorn app.main:app --reload`)
4. Good answers with citations (curl)
5. Out-of-corpus refusal demo
6. LangGraph diagram walkthrough
