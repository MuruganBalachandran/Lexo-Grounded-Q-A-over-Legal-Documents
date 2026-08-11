"""
backend/pipeline/graph/graph.py
──────────────────
LangGraph StateGraph wiring and compilation.

Flow
────
                    ┌───────────┐
        START  ──►  │  retrieve │
                    └─────┬─────┘
                          │
                    ┌─────▼──────────┐
                    │  grade_chunks  │
                    └─────┬──────────┘
                          │
             ┌────────────▼──────────────┐
             │    _route_after_grade      │  (conditional edge)
             │    "sufficient"  │  "retry_or_refuse"
             └────────┬─────────┴───────────┐
                      │                     │
               ┌──────▼──────┐    ┌─────────▼──────────────┐
               │   generate  │    │  retry_count < MAX?     │
               └──────┬──────┘    │  yes → retrieve         │
                      │           │  no  → not_found        │
                    END           └────────────────────────┘

Loop guard: MAX_RETRIES (default 2) prevents infinite cycles.
"""

from __future__ import annotations

from typing import Literal

from langgraph.graph import END, START, StateGraph

from core.config import settings
from pipeline.graph.nodes import generate, grade_chunks, not_found, retrieve
from pipeline.graph.state import QAState

# ── Routing function (conditional edge) ───────────────────────────────────────

def _route_after_grade(
    state: QAState,
) -> Literal["generate", "retrieve", "not_found"]:
    """
    Decide next node based on grade result and retry budget.

    - "sufficient"   → generate (answer found)
    - "insufficient" + retries left → retrieve (try again)
    - "insufficient" + no retries left → not_found (give up honestly)
    """
    grade = state.get("grade", "insufficient")
    retry_count = state.get("retry_count", 0)

    if grade == "sufficient":
        return "generate"

    if retry_count < settings.max_retries:
        return "retrieve"

    return "not_found"


# ── Retry counter middleware ───────────────────────────────────────────────────

def _increment_retry(state: QAState) -> dict:
    """
    Thin passthrough node that bumps retry_count before looping back to retrieve.
    This keeps the loop guard logic in one place.
    """
    return {"retry_count": state.get("retry_count", 0) + 1}


# ── Graph construction ────────────────────────────────────────────────────────

def build_graph() -> StateGraph:
    builder = StateGraph(QAState)

    # Register nodes
    builder.add_node("retrieve", retrieve)
    builder.add_node("grade_chunks", grade_chunks)
    builder.add_node("generate", generate)
    builder.add_node("not_found", not_found)
    builder.add_node("increment_retry", _increment_retry)

    # Entry point
    builder.add_edge(START, "retrieve")

    # retrieve → grade_chunks (always)
    builder.add_edge("retrieve", "grade_chunks")

    # grade_chunks → conditional branch
    builder.add_conditional_edges(
        "grade_chunks",
        _route_after_grade,
        {
            "generate": "generate",
            "retrieve": "increment_retry",   # bump counter, then loop
            "not_found": "not_found",
        },
    )

    # Retry loop: increment_retry → retrieve
    builder.add_edge("increment_retry", "retrieve")

    # Terminal nodes
    builder.add_edge("generate", END)
    builder.add_edge("not_found", END)

    return builder


# ── Compiled app (cached singleton) ───────────────────────────────────────────

_compiled_graph = None


def get_graph():
    """Return the compiled LangGraph app (singleton)."""
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_graph().compile()
    return _compiled_graph
