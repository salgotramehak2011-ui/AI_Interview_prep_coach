"""Text chunking for RAG pipeline."""

from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from loguru import logger

from app.config import get_settings


class TextChunker:
    """Split documents using RecursiveCharacterTextSplitter."""

    def __init__(self) -> None:
        settings = get_settings()
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        if not documents:
            logger.warning("No documents to chunk")
            return []
        chunks = self.splitter.split_documents(documents)
        logger.info("Created {} chunks from {} documents", len(chunks), len(documents))
        return chunks
