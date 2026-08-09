"""
app/main.py
───────────
FastAPI application entry point.

Routes
──────
GET  /           → health check
POST /ask        → Q&A via LangGraph (main endpoint)
POST /ingest     → run ingest pipeline (convenience for reviewers)

Run:
    uvicorn app.main:app --reload
"""

from __future__ import annotations

import traceback
from contextlib import asynccontextmanager
from typing import Any, Dict

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from app.config import settings
from app.graph.graph import get_graph
from app.graph.state import QAState
from app.ingest import run_ingest
from app.models import AskRequest, AskResponse, Citation, HealthResponse, IngestResponse


# ── Lifespan: pre-warm the graph on startup ────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Compile graph once on startup so first request isn't slow
    get_graph()
    print("[startup] LangGraph compiled and ready.")
    yield


# ── App factory ───────────────────────────────────────────────────────────────

app = FastAPI(
    title="Legixo Document Q&A API",
    description=(
        "Answer questions strictly from a legal document corpus. "
        "Powered by LangGraph + Gemini + Pinecone."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# ── Global error handler ──────────────────────────────────────────────────────

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"},
    )


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    """Service health check."""
    return HealthResponse()


@app.post("/ask", response_model=AskResponse, tags=["Q&A"])
async def ask(request: AskRequest) -> AskResponse:
    """
    Answer a question from the legal document corpus.

    - Retrieves relevant chunks from Pinecone.
    - Grades chunk relevance using Gemini (LLM-as-judge).
    - Generates a grounded answer with source citations.
    - If no relevant chunks found after retries, returns an honest refusal.

    **Request body:**
    ```json
    { "question": "What is the notice period at Bluecrest?" }
    ```

    **Response:**
    ```json
    {
      "answer": "...",
      "citations": [{"source_file": "02_...", "chunk_id": "...", "snippet": "...", "score": 0.91}],
      "grounded": true,
      "trace": ["retrieve", "grade_chunks", "generate"]
    }
    ```
    """
    if not request.question.strip():
        raise HTTPException(status_code=422, detail="Question must not be empty.")

    graph = get_graph()

    # Initialise state
    initial_state: Dict[str, Any] = {
        "question": request.question.strip(),
        "retrieved_chunks": [],
        "grade": "",
        "graded_chunks": [],
        "answer": "",
        "citations": [],
        "grounded": False,
        "retry_count": 0,
        "trace": [],
    }

    try:
        final_state: QAState = graph.invoke(initial_state)
    except Exception as exc:
        traceback.print_exc()
        raise HTTPException(
            status_code=502,
            detail=f"Graph execution failed: {str(exc)}",
        )

    citations = [
        Citation(
            source_file=c.get("source_file", ""),
            chunk_id=c.get("chunk_id", ""),
            snippet=c.get("snippet", ""),
            score=float(c.get("score", 0.0)),
        )
        for c in final_state.get("citations", [])
    ]

    return AskResponse(
        answer=final_state.get("answer", ""),
        citations=citations,
        grounded=final_state.get("grounded", False),
        trace=final_state.get("trace", []),
    )


@app.post("/ingest", response_model=IngestResponse, tags=["Ingest"])
async def ingest() -> IngestResponse:
    """
    Load the corpus from disk, embed chunks, and upsert to Pinecone.

    Safe to call multiple times — uses deterministic chunk IDs so re-running
    overwrites existing vectors rather than duplicating them.

    CLI alternative:
        python -m app.ingest [--dir path/to/corpus]
    """
    try:
        result = run_ingest()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Ingest failed: {str(exc)}")

    return IngestResponse(
        files_processed=result["files_processed"],
        chunks_upserted=result["chunks_upserted"],
    )
