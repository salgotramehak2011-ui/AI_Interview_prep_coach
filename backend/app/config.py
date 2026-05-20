"""Application configuration loaded from environment variables."""

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration for the interview coach backend."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "AI Interview Preparation Coach"
    API_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_PREFIX: str = "/api/v1"

    # Paths (backend/ is parent of app/)
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATASETS_DIR: Path = BASE_DIR / "datasets"
    VECTOR_DB_DIR: Path = BASE_DIR / "vector_db" / "chroma"
    DATA_DIR: Path = BASE_DIR / "data"
    LOGS_DIR: Path = BASE_DIR / "logs"

    # RAG
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    RETRIEVAL_K: int = 4

    # Ollama / LLM
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_PRIMARY_MODEL: str = "llama3.2"
    OLLAMA_FALLBACK_MODEL: str = "phi3:mini"
    LLM_TEMPERATURE: float = 0.7
    LLM_TIMEOUT: int = 120

    # Hugging Face
    HF_TOKEN: Optional[str] = None
    HF_MODEL_ID: str = "meta-llama/Llama-3.3-70B-Instruct"
    HF_API_BASE_URL: str = "https://router.huggingface.co/v1"

    # SQLite
    SQLITE_DB_PATH: Optional[Path] = None

    # CORS
    CORS_ORIGINS: str = "http://localhost:8501,http://127.0.0.1:8501"

    @property
    def database_path(self) -> Path:
        if self.SQLITE_DB_PATH:
            return Path(self.SQLITE_DB_PATH)
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        return self.DATA_DIR / "interview_coach.db"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    def vector_store_path(self, domain: str) -> Path:
        return self.VECTOR_DB_DIR / domain

    def dataset_path(self, domain: str) -> Path:
        return self.DATASETS_DIR / domain


@lru_cache
def get_settings() -> Settings:
    return Settings()
