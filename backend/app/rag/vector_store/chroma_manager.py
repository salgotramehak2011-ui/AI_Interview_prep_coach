"""ChromaDB vector store management per domain."""

from pathlib import Path
from typing import List, Optional

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore
from loguru import logger

from app.config import get_settings
from app.core.constants import CHROMA_COLLECTION_PREFIX
from app.rag.embeddings.embedding_model import get_embedding_model


class ChromaManager:
    """Manage domain-specific persistent ChromaDB collections."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.embeddings = get_embedding_model()

    def collection_name(self, domain: str) -> str:
        return f"{CHROMA_COLLECTION_PREFIX}{domain}"

    def persist_path(self, domain: str) -> Path:
        path = self.settings.vector_store_path(domain)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def get_vectorstore(self, domain: str) -> Chroma:
        return Chroma(
            collection_name=self.collection_name(domain),
            embedding_function=self.embeddings,
            persist_directory=str(self.persist_path(domain)),
        )

    def add_documents(self, domain: str, documents: List[Document]) -> int:
        if not documents:
            return 0
        store = self.get_vectorstore(domain)
        ids = store.add_documents(documents)
        logger.info("Added {} documents to Chroma collection for {}", len(ids), domain)
        return len(ids)

    def delete_collection(self, domain: str) -> None:
        path = self.persist_path(domain)
        store = self.get_vectorstore(domain)
        try:
            store.delete_collection()
        except Exception as exc:
            logger.warning("Could not delete collection {}: {}", domain, exc)
        # Remove persisted files for clean rebuild
        import shutil

        if path.exists():
            shutil.rmtree(path, ignore_errors=True)
            path.mkdir(parents=True, exist_ok=True)
        logger.info("Reset vector store for domain: {}", domain)

    def as_retriever(self, domain: str, k: Optional[int] = None):
        k = k or self.settings.RETRIEVAL_K
        return self.get_vectorstore(domain).as_retriever(search_kwargs={"k": k})

    def similarity_search(self, domain: str, query: str, k: Optional[int] = None) -> List[Document]:
        k = k or self.settings.RETRIEVAL_K
        return self.get_vectorstore(domain).similarity_search(query, k=k)
