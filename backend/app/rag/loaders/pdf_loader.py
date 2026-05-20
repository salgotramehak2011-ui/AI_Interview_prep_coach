"""PDF document loading for RAG ingestion."""

from pathlib import Path
from typing import List

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.documents import Document
from loguru import logger

from app.utils.cleaner import clean_pdf_text


class DocumentLoaderService:
    """Load PDF and text files from a directory."""

    SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md"}

    def load_directory(self, directory: Path) -> List[Document]:
        documents: List[Document] = []
        if not directory.exists():
            logger.warning("Dataset directory does not exist: {}", directory)
            return documents

        for path in sorted(directory.rglob("*")):
            if path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
                continue
            try:
                docs = self.load_file(path)
                documents.extend(docs)
                logger.info("Loaded {} chunks from {}", len(docs), path.name)
            except Exception as exc:
                logger.error("Failed to load {}: {}", path, exc)

        return documents

    def load_file(self, file_path: Path) -> List[Document]:
        suffix = file_path.suffix.lower()
        if suffix == ".pdf":
            loader = PyPDFLoader(str(file_path))
            docs = loader.load()
            for doc in docs:
                doc.page_content = clean_pdf_text(doc.page_content)
                doc.metadata["source"] = str(file_path)
                doc.metadata["file_type"] = "pdf"
            return docs

        loader = TextLoader(str(file_path), encoding="utf-8")
        docs = loader.load()
        for doc in docs:
            doc.metadata["source"] = str(file_path)
            doc.metadata["file_type"] = suffix.lstrip(".")
        return docs
