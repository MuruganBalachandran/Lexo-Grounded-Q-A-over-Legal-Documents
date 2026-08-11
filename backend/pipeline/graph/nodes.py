"""
backend/pipeline/graph/nodes.py
──────────────────
LangGraph node implementations.

Node contract: each node receives QAState and returns a dict of
fields to merge back into state (partial update pattern).

Nodes
─────
1. retrieve      – vector search Pinecone for top-k chunks
2. grade_chunks  – LLM binary judgment: sufficient / insufficient
3. generate      – grounded answer + citations (good path)
4. not_found     – polite refusal with no fabricated answer (bad path)
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List

import requests

from core.config import settings
from core.embeddings import embed_query
from pipeline.graph.state import QAState, RetrievedChunk
from core.pinecone_client import get_index

_CHAT_URL = (
    f"https://generativelanguage.googleapis.com/v1/models/"
    f"gemini-2.5-flash:generateContent"
)


def _llm_invoke(prompt: str, max_retries: int = 4) -> str:
    """Call the Gemini generateContent REST endpoint directly (v1, no SDK).
    Retries with exponential backoff on 429 Too Many Requests.
    """
    import time
    delay = 5
    for attempt in range(max_retries):
        resp = requests.post(
            _CHAT_URL,
            params={"key": settings.gemini_api_key},
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0},
            },
            timeout=60,
        )
        if resp.status_code == 429:
            wait = delay * (2 ** attempt)
            print(f"[llm] Rate limited (429) — retrying in {wait}s ...")
            time.sleep(wait)
            continue
        resp.raise_for_status()
        return resp.json()["candidates"][0]["content"]["parts"][0]["text"]
    raise RuntimeError(f"LLM call failed after {max_retries} retries due to rate limiting.")


# ═══════════════════════════════════════════════════════════════════════════════
# Node 1 — retrieve
# ═══════════════════════════════════════════════════════════════════════════════

def retrieve(state: QAState) -> Dict[str, Any]:
    """
    Query Pinecone with the user question and return top-k chunks.

    On retry (retry_count > 0) the question is passed as-is; a more
    sophisticated system could rewrite the query here.
    """
    question = state["question"]
    query_vec = embed_query(question)

    index = get_index()
    response = index.query(
        vector=query_vec,
        top_k=settings.top_k,
        include_metadata=True,
    )

    chunks: List[RetrievedChunk] = []
    for match in response.matches:
        meta = match.metadata or {}
        chunks.append(
            RetrievedChunk(
                chunk_id=meta.get("chunk_id", match.id),
                source_file=meta.get("source_file", "unknown"),
                section_title=meta.get("section_title", ""),
                text=meta.get("text", ""),
                score=float(match.score or 0.0),
            )
        )

    trace = list(state.get("trace", []))
    trace.append("retrieve")

    return {
        "retrieved_chunks": chunks,
        "trace": trace,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Node 2 — grade_chunks
# ═══════════════════════════════════════════════════════════════════════════════

_GRADE_PROMPT = """\
You are a strict document relevance judge for a legal Q&A system.

User question:
{question}

Retrieved document chunks (JSON):
{chunks_json}

Task:
For each chunk, decide whether it contains information that directly helps
answer the user's question. Be strict: if the chunk is only tangentially
related or does not address the question, mark it irrelevant.

Return a JSON object with exactly two keys:
{{
  "grade": "sufficient" | "insufficient",
  "relevant_ids": ["chunk_id_1", ...]
}}

"sufficient" means at least one chunk contains enough direct evidence to
compose a factual answer. "insufficient" means none of the chunks contain
enough direct evidence.

Do NOT include any explanation — respond with JSON only.
"""


def grade_chunks(state: QAState) -> Dict[str, Any]:
    """
    LLM-based relevance grading.

    Returns:
        grade        – "sufficient" or "insufficient"
        graded_chunks – subset of retrieved_chunks that are relevant
    """
    question = state["question"]
    retrieved = state.get("retrieved_chunks", [])

    if not retrieved:
        trace = list(state.get("trace", []))
        trace.append("grade_chunks")
        return {"grade": "insufficient", "graded_chunks": [], "trace": trace}

    chunks_json = json.dumps(
        [{"chunk_id": c["chunk_id"], "text": c["text"]} for c in retrieved],
        ensure_ascii=False,
        indent=2,
    )

    prompt = _GRADE_PROMPT.format(question=question, chunks_json=chunks_json)
    raw = _llm_invoke(prompt).strip()

    # Strip markdown code fences if present
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    try:
        result = json.loads(raw)
        grade = result.get("grade", "insufficient")
        relevant_ids = set(result.get("relevant_ids", []))
    except (json.JSONDecodeError, AttributeError):
        # If parsing fails, treat as insufficient to be safe
        grade = "insufficient"
        relevant_ids = set()

    graded_chunks = [c for c in retrieved if c["chunk_id"] in relevant_ids]

    trace = list(state.get("trace", []))
    trace.append("grade_chunks")

    return {
        "grade": grade,
        "graded_chunks": graded_chunks,
        "trace": trace,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Node 3 — generate
# ═══════════════════════════════════════════════════════════════════════════════

_GENERATE_PROMPT = """\
You are a precise legal document assistant. Answer the user's question
using ONLY the information in the provided document chunks.

Rules:
1. Base your answer strictly on the chunks — do not invent, assume, or use
   outside knowledge.
2. If the chunks give a partial answer, state what is found and clearly note
   what is not addressed.
3. Write in plain, clear language. Use bullet points if listing multiple facts.
4. Do NOT mention "chunks", "documents", or the retrieval process in your answer.

User question:
{question}

Relevant document chunks:
{chunks_text}

Answer:
"""


def generate(state: QAState) -> Dict[str, Any]:
    """
    Compose a grounded answer strictly from the graded-good chunks.
    Returns answer text + citations.
    """
    question = state["question"]
    graded = state.get("graded_chunks", [])

    # Build the context block shown to the LLM
    chunks_text = "\n\n---\n\n".join(
        f"[{c['source_file']} / {c['section_title']}]\n{c['text']}"
        for c in graded
    )

    prompt = _GENERATE_PROMPT.format(question=question, chunks_text=chunks_text)
    answer = _llm_invoke(prompt).strip()

    citations = [
        {
            "source_file": c["source_file"],
            "chunk_id": c["chunk_id"],
            "snippet": c["text"][:300],  # first 300 chars as preview
            "score": round(c["score"], 4),
        }
        for c in graded
    ]

    trace = list(state.get("trace", []))
    trace.append("generate")

    return {
        "answer": answer,
        "citations": citations,
        "grounded": True,
        "trace": trace,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Node 4 — not_found
# ═══════════════════════════════════════════════════════════════════════════════

def not_found(state: QAState) -> Dict[str, Any]:
    """
    Return a clear, honest refusal when the corpus cannot answer the question.
    No fabrication. No invented citations.
    """
    answer = (
        "I cannot find an answer to this question in the provided documents. "
        "The corpus does not appear to contain information relevant to your query. "
        "Please consult the original source documents or a qualified professional."
    )

    trace = list(state.get("trace", []))
    trace.append("not_found")

    return {
        "answer": answer,
        "citations": [],
        "grounded": False,
        "trace": trace,
    }
