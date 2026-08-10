"""
app/chunker.py
──────────────
Section-based chunker for the legal markdown corpus.

Strategy: split each file on `## ` headings (level-2 markdown headers).
Each section becomes one chunk. This is ideal for the corpus because:
  - The files are short (300–700 chars each).
  - Each section directly answers one or more gold-set questions.
  - Keeping sections whole avoids splitting facts across chunks.

Chunk ID scheme (deterministic / idempotent):
  chunk_id = f"{source_file}::{section_slug}"
  where section_slug = lower-cased, space→underscore title of the ## heading,
  or "header" for text above the first ## heading.

Re-running ingest with the same corpus produces identical chunk_ids,
so Pinecone upsert overwrites existing vectors rather than duplicating.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class Chunk:
    chunk_id: str          # deterministic, unique per source+section
    source_file: str       # filename only, e.g. "01_matter_memo_arvind_v_northfield.md"
    section_title: str     # the ## heading text (or "header" for preamble)
    text: str              # verbatim section text (CRLF → LF normalised)


def _slugify(title: str) -> str:
    """Convert a heading like 'Key dates' → 'key_dates'."""
    slug = title.strip().lower()
    slug = re.sub(r"[^a-z0-9]+", "_", slug)
    return slug.strip("_") or "section"


def chunk_file(file_path: Path) -> List[Chunk]:
    """
    Split a single markdown file into section-level chunks.

    Sections are delimited by `## ` level-2 headings.
    Text above the first `## ` is kept as a "header" chunk (contains
    the document title and top-level metadata lines).
    """
    raw = file_path.read_text(encoding="utf-8")
    # Normalise line endings
    text = raw.replace("\r\n", "\n").replace("\r", "\n")

    source_file = file_path.name
    chunks: List[Chunk] = []

    # Split on lines that start with '## '
    # Keep the delimiter as the start of each section
    parts = re.split(r"(?m)^(## .+)$", text)
    # parts alternates: [pre_text, heading, body, heading, body, ...]

    # Pre-heading content (document title + metadata)
    preamble = parts[0].strip()
    if preamble:
        chunks.append(
            Chunk(
                chunk_id=f"{source_file}::header",
                source_file=source_file,
                section_title="header",
                text=preamble,
            )
        )

    # Process heading + body pairs
    it = iter(parts[1:])
    for heading in it:
        body = next(it, "").strip()
        section_title = heading.lstrip("#").strip()
        combined = f"{heading}\n\n{body}".strip()
        if combined:
            chunks.append(
                Chunk(
                    chunk_id=f"{source_file}::{_slugify(section_title)}",
                    source_file=source_file,
                    section_title=section_title,
                    text=combined,
                )
            )

    return chunks


def chunk_corpus(corpus_dir: str) -> List[Chunk]:
    """
    Load and chunk all .md files in corpus_dir.
    Returns chunks sorted by (source_file, section order).
    """
    base = Path(corpus_dir)
    if not base.exists():
        raise FileNotFoundError(f"Corpus directory not found: {base.resolve()}")

    all_chunks: List[Chunk] = []
    md_files = sorted(base.glob("*.md"))

    if not md_files:
        raise ValueError(f"No .md files found in {base.resolve()}")

    for md_file in md_files:
        file_chunks = chunk_file(md_file)
        all_chunks.extend(file_chunks)
        print(f"  [chunker] {md_file.name} -> {len(file_chunks)} chunk(s)")

    return all_chunks
