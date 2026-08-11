"""
backend/pipeline/ingest.py
─────────────
Ingest pipeline: load → chunk → embed → upsert to Pinecone.

CLI usage (from project root):
    python -m backend.pipeline.ingest

API usage:
    POST /ingest  (wired in backend/api/routes/ingest.py)

Idempotency guarantee
─────────────────────
Chunk IDs are deterministic (see backend/pipeline/chunker.py).
Running ingest twice on the same corpus produces identical IDs,
so Pinecone's upsert overwrites existing vectors — vector count
stays the same after a second run.

Pinecone metadata schema per vector
────────────────────────────────────
{
    "chunk_id":      str,   # e.g. "01_matter_memo_arvind_v_northfield.md::key_dates"
    "source_file":   str,   # e.g. "01_matter_memo_arvind_v_northfield.md"
    "section_title": str,   # e.g. "Key dates"
    "text":          str,   # full verbatim section text (used for citation display)
}
"""

from __future__ import annotations

import math
from typing import List

from pipeline.chunker import Chunk, chunk_corpus
from core.config import settings
from core.embeddings import embed_documents
from core.pinecone_client import get_index, get_or_create_index

# Pinecone recommends batch sizes of 100 or fewer
_BATCH_SIZE = 50


def _batch(lst: list, size: int):
    """Yield successive chunks of `size` from `lst`."""
    for i in range(0, len(lst), size):
        yield lst[i : i + size]


def run_ingest(corpus_dir: str | None = None) -> dict:
    """
    Full ingest pipeline.

    Returns a dict with:
        files_processed: int
        chunks_upserted: int
    """
    corpus_dir = corpus_dir or settings.corpus_dir

    print(f"\n[ingest] Starting ingest from '{corpus_dir}' ...")

    # 1. Ensure Pinecone index exists
    get_or_create_index()
    index = get_index()

    # 2. Load + chunk corpus
    chunks: List[Chunk] = chunk_corpus(corpus_dir)
    print(f"[ingest] Total chunks: {len(chunks)}")

    # 3. Embed + upsert in batches
    total_upserted = 0
    num_batches = math.ceil(len(chunks) / _BATCH_SIZE)

    for batch_num, batch in enumerate(_batch(chunks, _BATCH_SIZE), start=1):
        texts = [c.text for c in batch]
        print(f"[ingest] Embedding batch {batch_num}/{num_batches} ({len(texts)} chunks) ...")
        vectors = embed_documents(texts)

        pinecone_vectors = [
            {
                "id": chunk.chunk_id,
                "values": vec,
                "metadata": {
                    "chunk_id": chunk.chunk_id,
                    "source_file": chunk.source_file,
                    "section_title": chunk.section_title,
                    "text": chunk.text,
                },
            }
            for chunk, vec in zip(batch, vectors)
        ]

        index.upsert(vectors=pinecone_vectors)
        total_upserted += len(pinecone_vectors)
        print(f"[ingest] Upserted {total_upserted} vectors so far ...")

    # Unique source files
    source_files = sorted({c.source_file for c in chunks})
    print(f"\n[ingest] Done. {total_upserted} vectors upserted from {len(source_files)} file(s).")

    return {
        "files_processed": len(source_files),
        "chunks_upserted": total_upserted,
    }


# ── CLI entry point ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Ingest legal markdown corpus into Pinecone.")
    parser.add_argument(
        "--dir",
        default=None,
        help="Path to corpus directory (default: value of CORPUS_DIR in .env)",
    )
    args = parser.parse_args()

    result = run_ingest(corpus_dir=args.dir)
    print(f"\nResult: {result}")
