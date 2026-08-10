"""
backend/api/schemas/qa.py
─────────────
Pydantic request/response schemas for the FastAPI layer.
Kept separate from graph state to decouple HTTP concerns from graph internals.
"""

from __future__ import annotations

from typing import Any, Dict, List

from pydantic import BaseModel, Field


# ── /ask ──────────────────────────────────────────────────────────────────────

class AskRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=3,
        max_length=2000,
        examples=["What notice period applies when Bluecrest ends the employment agreement?"],
        description="Natural language question to answer from the document corpus.",
    )


class Citation(BaseModel):
    source_file: str = Field(description="Filename of the source document.")
    chunk_id: str = Field(description="Deterministic chunk identifier (source_file::section_slug).")
    snippet: str = Field(description="First 300 chars of the chunk used to compose the answer.")
    score: float = Field(default=0.0, description="Cosine similarity score from Pinecone.")


class AskResponse(BaseModel):
    answer: str = Field(description="Answer grounded in corpus chunks, or refusal message.")
    citations: List[Citation] = Field(
        default_factory=list,
        description="Chunks that directly supported the answer. Empty on refusal.",
    )
    grounded: bool = Field(
        description="True = answer grounded in corpus. False = refused / not found in docs.",
    )
    trace: List[str] = Field(
        default_factory=list,
        description="Ordered list of LangGraph nodes visited (for debugging/observability).",
    )


# ── /ingest ───────────────────────────────────────────────────────────────────

class IngestResponse(BaseModel):
    files_processed: int = Field(description="Number of .md files loaded from corpus.")
    chunks_upserted: int = Field(description="Number of vectors upserted to Pinecone.")
    message: str = Field(default="Ingest complete.")


# ── /health ───────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "legixo-qa-api"
    version: str = "1.0.0"
