"""
app/embeddings.py
─────────────────
Thin wrapper around the Gemini Embeddings API via langchain-google-genai.

model: models/text-embedding-004
  - Output dimension: 768
  - task_type: "RETRIEVAL_DOCUMENT" for ingest, "RETRIEVAL_QUERY" for queries

Usage:
    from app.embeddings import embed_documents, embed_query

    doc_vectors = embed_documents(["text one", "text two"])
    query_vector = embed_query("What is the notice period?")
"""

from __future__ import annotations

import os
from typing import List

from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.config import settings

# Set the API key in env so langchain picks it up
os.environ.setdefault("GOOGLE_API_KEY", settings.gemini_api_key)


def _make_embedder(task_type: str) -> GoogleGenerativeAIEmbeddings:
    return GoogleGenerativeAIEmbeddings(
        model=settings.embed_model,
        google_api_key=settings.gemini_api_key,
        task_type=task_type,
    )


def embed_documents(texts: List[str]) -> List[List[float]]:
    """
    Embed a list of document chunks.
    Uses task_type='RETRIEVAL_DOCUMENT' for optimal asymmetric retrieval.
    """
    embedder = _make_embedder("RETRIEVAL_DOCUMENT")
    return embedder.embed_documents(texts)


def embed_query(text: str) -> List[float]:
    """
    Embed a single user query.
    Uses task_type='RETRIEVAL_QUERY' to match the asymmetric retrieval setup.
    """
    embedder = _make_embedder("RETRIEVAL_QUERY")
    return embedder.embed_query(text)
