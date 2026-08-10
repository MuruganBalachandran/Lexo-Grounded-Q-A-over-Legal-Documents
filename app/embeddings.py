"""
app/embeddings.py
─────────────────
Thin wrapper around the Gemini Embeddings REST API.
Calls the v1 REST endpoint directly via `requests` to avoid SDK version
incompatibilities between google-genai (v1beta) and google-generativeai.

model: models/gemini-embedding-001
  - Output dimension: 3072
  - task_type: "RETRIEVAL_DOCUMENT" for ingest, "RETRIEVAL_QUERY" for queries

Usage:
    from app.embeddings import embed_documents, embed_query

    doc_vectors = embed_documents(["text one", "text two"])
    query_vector = embed_query("What is the notice period?")
"""

from __future__ import annotations

from typing import List

import requests

from app.config import settings

_BASE = "https://generativelanguage.googleapis.com/v1"


def _model_id() -> str:
    """Return the bare model id, stripping the 'models/' prefix if present."""
    return settings.embed_model.replace("models/", "")


def embed_documents(texts: List[str]) -> List[List[float]]:
    """
    Embed a list of document chunks via batchEmbedContents.
    Uses task_type='RETRIEVAL_DOCUMENT' for optimal asymmetric retrieval.
    """
    model = _model_id()
    url = f"{_BASE}/models/{model}:batchEmbedContents"
    params = {"key": settings.gemini_api_key}

    body = {
        "requests": [
            {
                "model": f"models/{model}",
                "content": {"parts": [{"text": text}]},
                "taskType": "RETRIEVAL_DOCUMENT",
            }
            for text in texts
        ]
    }

    response = requests.post(url, json=body, params=params, timeout=120)
    response.raise_for_status()
    data = response.json()
    return [emb["values"] for emb in data["embeddings"]]


def embed_query(text: str) -> List[float]:
    """
    Embed a single user query via embedContent.
    Uses task_type='RETRIEVAL_QUERY' to match the asymmetric retrieval setup.
    """
    model = _model_id()
    url = f"{_BASE}/models/{model}:embedContent"
    params = {"key": settings.gemini_api_key}

    body = {
        "model": f"models/{model}",
        "content": {"parts": [{"text": text}]},
        "taskType": "RETRIEVAL_QUERY",
    }

    response = requests.post(url, json=body, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()
    return data["embedding"]["values"]
