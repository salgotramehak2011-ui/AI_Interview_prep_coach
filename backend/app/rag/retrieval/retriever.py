"""Domain-based dynamic retriever selection."""

from functools import lru_cache
from typing import List, Optional

from langchain_core.documents import Document
from loguru import logger

from app.config import get_settings
from app.rag.vector_store.chroma_manager import ChromaManager
from app.utils.validators import is_valid_domain


class DomainRetriever:
    """Select and use the correct retriever for each interview domain."""

    def __init__(self) -> None:
        self.chroma = ChromaManager()
        self.settings = get_settings()

    def get_retriever(self, domain: str, k: Optional[int] = None):
        if not is_valid_domain(domain):
            raise ValueError(f"Invalid domain: {domain}")
        return self.chroma.as_retriever(domain, k=k)

    def retrieve(self, domain: str, query: str, k: Optional[int] = None) -> List[Document]:
        if not is_valid_domain(domain):
            raise ValueError(f"Invalid domain: {domain}")
        k = k or self.settings.RETRIEVAL_K
        logger.debug("Retrieving top-{} docs for domain={} query={}", k, domain, query[:80])
        return self.chroma.similarity_search(domain, query, k=k)

    def retrieve_context_string(self, domain: str, query: str, k: Optional[int] = None) -> str:
        docs = self.retrieve(domain, query, k=k)
        if not docs:
            return ""
        parts = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get("source", "unknown")
            parts.append(f"[{i}] (source: {source})\n{doc.page_content}")
        return "\n\n---\n\n".join(parts)


@lru_cache
def get_domain_retriever() -> DomainRetriever:
    return DomainRetriever()
