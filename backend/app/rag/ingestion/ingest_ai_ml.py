"""Ingest AI/ML domain documents into ChromaDB."""

import sys
from pathlib import Path

# Allow running as script: python -m app.rag.ingestion.ingest_ai_ml
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from app.core.constants import Domain
from app.services.rag_service import RAGService
from loguru import logger


def main() -> None:
    service = RAGService()
    result = service.ingest_domain(Domain.AI_ML.value, force_rebuild=True)
    logger.info("AI/ML ingestion complete: {}", result)


if __name__ == "__main__":
    main()
