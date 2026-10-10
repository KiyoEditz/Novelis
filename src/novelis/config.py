"""Novelis Configuration Module
Provides centralized runtime settings for LLM, Memory, Embeddings, and Storage.
"""

from pathlib import Path
import os
from typing import Literal

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class NovelisConfig:
    """Application configuration container."""

    # Project directories
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATA_DIR: Path = Path(os.getenv("DATA_DIR", "./data")).resolve()

    # Story Bible & Vector Database paths
    STORY_BIBLE_PATH: Path = DATA_DIR / "story_bible.db"
    LANCEDB_DIR: Path = DATA_DIR / "lancedb"

    # LLM Settings (Primary: Gemini 3.8)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

    # LLM Settings (Secondary: OpenAI Compatible)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # Embedding & Reranker Settings
    EMBEDDING_MODE: Literal["local", "remote"] = os.getenv("EMBEDDING_MODE", "local").lower()  # type: ignore
    LOCAL_EMBEDDING_MODEL: str = os.getenv("LOCAL_EMBEDDING_MODEL", "BAAI/bge-m3")
    LOCAL_RERANKER_MODEL: str = os.getenv("LOCAL_RERANKER_MODEL", "BAAI/bge-reranker-v2-m3")
    REMOTE_WORKER_URL: str = os.getenv("REMOTE_WORKER_URL", "")

    @classmethod
    def ensure_directories(cls) -> None:
        """Ensures that required data directories exist."""
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
        cls.LANCEDB_DIR.mkdir(parents=True, exist_ok=True)

config = NovelisConfig()
