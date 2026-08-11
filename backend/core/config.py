"""
backend/core/config.py
──────────────────────
Centralised settings loaded from .env via pydantic-settings.
Every other module imports `settings` from here — no direct os.environ calls.
"""
1
from functools import lru_cache
import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_PATH = Path(__file__).parent.parent / ".env"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_ENV_PATH,
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── API Keys ──────────────────────────────────────────────────────────────
    gemini_api_key: str
    pinecone_api_key: str

    # ── Pinecone ──────────────────────────────────────────────────────────────
    pinecone_index_name: str = "legixo-qa"
    pinecone_cloud: str = "aws"
    pinecone_region: str = "us-east-1"

    # ── Gemini Models ─────────────────────────────────────────────────────────
    # gemini-embedding-001 produces 3072-dimensional vectors
    embed_model: str = "models/gemini-embedding-001"
    # Chat/generation model
    chat_model: str = "gemini-3.6-flash"

    # ── Retrieval ────────────────────────────────────────────────────────────
    top_k: int = 5
    max_retries: int = 2

    # ── Corpus ────────────────────────────────────────────────────────────────
    corpus_dir: str = "corpus"


@lru_cache
def get_settings() -> Settings:
    """Return a cached singleton Settings instance."""
    return Settings()


# Module-level singleton — import this everywhere
settings = get_settings()
