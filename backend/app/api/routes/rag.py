"""RAG API routes."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_rag_service
from app.schemas.rag_schema import IngestRequest, IngestResponse, RetrieveRequest, RetrieveResponse
from app.services.rag_service import RAGService
from loguru import logger

router = APIRouter(prefix="/rag", tags=["RAG"])


@router.post("/ingest", response_model=IngestResponse)
async def ingest_documents(
    request: IngestRequest,
    service: RAGService = Depends(get_rag_service),
):
    try:
        return service.ingest_domain(request.domain, force_rebuild=request.force_rebuild)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        logger.exception("Ingestion failed")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@router.post("/retrieve", response_model=RetrieveResponse)
async def retrieve_context(
    request: RetrieveRequest,
    service: RAGService = Depends(get_rag_service),
):
    try:
        return service.retrieve(request.domain, request.query, k=request.k)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        logger.exception("Retrieval failed")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))
