"""
app/config.py
─────────────
Centralised settings loaded from .env via pydantic-settings.
Every other module imports `settings` from here — no direct os.environ calls.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
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
    # text-embedding-004 produces 768-dimensional vectors
    embed_model: str = "models/text-embedding-004"
    chat_model: str = "gemini-1.5-flash"

    # ── Retrieval ────────────────────────────────────────────────────────────
    top_k: int = 5
    max_retries: int = 2

    # ── Corpus ────────────────────────────────────────────────────────────────
    corpus_dir: str = "gen_ai_takehome_sample_corpus"


@lru_cache
def get_settings() -> Settings:
    """Return a cached singleton Settings instance."""
    return Settings()


# Module-level singleton — import this everywhere
settings = get_settings()
