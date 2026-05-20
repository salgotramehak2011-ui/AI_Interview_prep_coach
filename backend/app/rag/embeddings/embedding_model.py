"""HuggingFace embedding model wrapper."""

from functools import lru_cache

from langchain_huggingface import HuggingFaceEmbeddings
from loguru import logger

from app.config import get_settings


@lru_cache
def get_embedding_model() -> HuggingFaceEmbeddings:
    """Return cached HuggingFace embeddings instance."""
    settings = get_settings()
    logger.info("Loading embedding model: {}", settings.EMBEDDING_MODEL)
    return HuggingFaceEmbeddings(
        model_name=settings.EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
