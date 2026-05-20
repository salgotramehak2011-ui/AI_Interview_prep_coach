"""RAG ingestion and retrieval service."""

from pathlib import Path

from loguru import logger

from app.config import get_settings
from app.rag.chunking.text_chunker import TextChunker
from app.rag.loaders.pdf_loader import DocumentLoaderService
from app.rag.retrieval.retriever import DomainRetriever
from app.rag.vector_store.chroma_manager import ChromaManager
from app.schemas.rag_schema import IngestResponse, RetrieveResponse
from app.utils.validators import is_valid_domain


class RAGService:
    """Orchestrate document ingestion and retrieval."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.loader = DocumentLoaderService()
        self.chunker = TextChunker()
        self.chroma = ChromaManager()
        self.retriever = DomainRetriever()

    def ingest_domain(self, domain: str, force_rebuild: bool = False) -> IngestResponse:
        if not is_valid_domain(domain):
            raise ValueError(f"Invalid domain: {domain}")

        dataset_path = self.settings.dataset_path(domain)
        if force_rebuild:
            self.chroma.delete_collection(domain)

        documents = self.loader.load_directory(dataset_path)
        if not documents:
            logger.warning("No documents found in {}", dataset_path)
            return IngestResponse(
                domain=domain,
                documents_processed=0,
                chunks_created=0,
                collection_name=self.chroma.collection_name(domain),
                message=f"No documents in {dataset_path}. Add PDF/TXT files and retry.",
            )

        chunks = self.chunker.chunk_documents(documents)
        for chunk in chunks:
            chunk.metadata["domain"] = domain

        count = self.chroma.add_documents(domain, chunks)
        return IngestResponse(
            domain=domain,
            documents_processed=len(documents),
            chunks_created=count,
            collection_name=self.chroma.collection_name(domain),
            message="Ingestion completed successfully",
        )

    def retrieve(self, domain: str, query: str, k: int | None = None) -> RetrieveResponse:
        docs = self.retriever.retrieve(domain, query, k=k)
        return RetrieveResponse(
            domain=domain,
            query=query,
            documents=[d.page_content for d in docs],
            metadatas=[d.metadata for d in docs],
        )

    def get_context(self, domain: str, query: str, k: int | None = None) -> str:
        return self.retriever.retrieve_context_string(domain, query, k=k)
