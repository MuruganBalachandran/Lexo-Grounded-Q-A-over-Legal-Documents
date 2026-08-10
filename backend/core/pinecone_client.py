"""
backend/core/pinecone_client.py
────────────────────────────────
Pinecone index management.

- get_or_create_index(): creates a serverless index if it doesn't exist.
- get_index(): returns a ready-to-use Pinecone Index object.

Gemini's `gemini-embedding-001` model outputs 3072-dimensional vectors,
so the index is created with dimension=3072 and cosine metric.

Idempotency: calling get_or_create_index() twice is safe — Pinecone's
describe_index_stats will confirm existence and the function returns
without re-creating.
"""

from __future__ import annotations

import time

from pinecone import Pinecone, ServerlessSpec

from backend.core.config import settings

# ── Embedding dimension for models/gemini-embedding-001 ──────────────────────
EMBED_DIM = 3072
METRIC = "cosine"


def get_pinecone_client() -> Pinecone:
    """Return an authenticated Pinecone client."""
    return Pinecone(api_key=settings.pinecone_api_key)


def get_or_create_index() -> None:
    """
    Create the Pinecone serverless index if it does not already exist.
    Safe to call on every startup or every ingest run.
    """
    pc = get_pinecone_client()
    existing = {idx.name for idx in pc.list_indexes()}

    if settings.pinecone_index_name not in existing:
        print(
            f"[pinecone] Creating index '{settings.pinecone_index_name}' "
            f"(dim={EMBED_DIM}, metric={METRIC}) ..."
        )
        pc.create_index(
            name=settings.pinecone_index_name,
            dimension=EMBED_DIM,
            metric=METRIC,
            spec=ServerlessSpec(
                cloud=settings.pinecone_cloud,
                region=settings.pinecone_region,
            ),
        )
        while not pc.describe_index(settings.pinecone_index_name).status["ready"]:
            print("[pinecone] Waiting for index to be ready ...")
            time.sleep(2)
        print("[pinecone] Index ready.")
    else:
        print(
            f"[pinecone] Index '{settings.pinecone_index_name}' already exists "
            f"— skipping creation."
        )


def get_index():
    """Return a Pinecone Index handle (index must already exist)."""
    pc = get_pinecone_client()
    return pc.Index(settings.pinecone_index_name)
