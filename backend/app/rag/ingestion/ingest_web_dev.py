"""Ingest Web Development domain documents into ChromaDB."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from app.core.constants import Domain
from app.services.rag_service import RAGService
from loguru import logger


def main() -> None:
    service = RAGService()
    result = service.ingest_domain(Domain.WEB_DEV.value, force_rebuild=True)
    logger.info("Web Dev ingestion complete: {}", result)


if __name__ == "__main__":
    main()
