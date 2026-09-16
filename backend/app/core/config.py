"""
Application Configuration Module.
Loads environment variables using Pydantic Settings.
"""

import os
from pathlib import Path
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base directory for the repository
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # General App Settings
    APP_NAME: str = "The Lenny Growth Assistant"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"

    # Database Settings
    DATABASE_URL: str = Field(
        default=f"sqlite:///{PROJECT_ROOT / 'data' / 'lenny_assistant.db'}",
        description="Database connection URL. Defaults to native local SQLite for zero-dependency execution.",
    )

    # Model Provider Settings
    DEFAULT_MODEL_PROVIDER: str = "ollama"  # "ollama", "anthropic", "openai", "mock"
    DEFAULT_MODEL_NAME: str = "llama3.2"

    # Ollama Local LLM Configuration
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_TIMEOUT_SECONDS: int = 45

    # Cloud LLM Configuration
    ANTHROPIC_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"

    # Knowledge Base & Retrieval
    TRANSCRIPTS_DATA_DIR: str = str(PROJECT_ROOT / "data" / "transcripts")
    FIXTURES_DATA_DIR: str = str(PROJECT_ROOT / "data" / "fixtures")
    VECTOR_STORE_DIR: str = str(PROJECT_ROOT / "data" / "vector_store")
    CHUNK_SIZE_WORDS: int = 380
    CHUNK_OVERLAP_WORDS: int = 50
    RETRIEVAL_TOP_K: int = 4
    RETRIEVAL_CONFIDENCE_THRESHOLD: float = 0.16

    @property
    def cors_origin_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


settings = Settings()

# Ensure directories exist
Path(settings.TRANSCRIPTS_DATA_DIR).mkdir(parents=True, exist_ok=True)
Path(settings.FIXTURES_DATA_DIR).mkdir(parents=True, exist_ok=True)
Path(settings.VECTOR_STORE_DIR).mkdir(parents=True, exist_ok=True)
Path(PROJECT_ROOT / "data").mkdir(parents=True, exist_ok=True)
