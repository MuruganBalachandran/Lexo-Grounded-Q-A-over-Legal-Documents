"""
backend/pipeline/graph/state.py
──────────────────
LangGraph state definition.

QAState is a TypedDict that flows through every node in the graph.
Nodes may read any field and write only to fields they own.
"""

from __future__ import annotations

from typing import Any, Dict, List, TypedDict


class RetrievedChunk(TypedDict):
    chunk_id: str
    source_file: str
    section_title: str
    text: str
    score: float


class QAState(TypedDict):
    # ── Input ─────────────────────────────────────────────────────────────────
    question: str                    # original user question

    # ── Retrieval ────────────────────────────────────────────────────────────
    retrieved_chunks: List[RetrievedChunk]  # raw Pinecone results

    # ── Grading ──────────────────────────────────────────────────────────────
    grade: str                       # "sufficient" | "insufficient"
    graded_chunks: List[RetrievedChunk]     # subset that passed grading

    # ── Generation ───────────────────────────────────────────────────────────
    answer: str                      # final answer text
    citations: List[Dict[str, Any]]  # [{source_file, chunk_id, snippet, score}]
    grounded: bool                   # True=answered, False=refused

    # ── Loop control ─────────────────────────────────────────────────────────
    retry_count: int                 # incremented on each insufficient retrieval

    # ── Observability ────────────────────────────────────────────────────────
    trace: List[str]                 # ordered list of node names visited
