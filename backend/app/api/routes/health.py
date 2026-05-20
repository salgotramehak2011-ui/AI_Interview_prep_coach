"""Health check endpoints."""

from fastapi import APIRouter

from app.config import get_settings

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    settings = get_settings()
    if settings.HF_TOKEN:
        llm_provider = f"Hugging Face ({settings.HF_MODEL_ID})"
    else:
        llm_provider = f"Ollama ({settings.OLLAMA_PRIMARY_MODEL})"
        
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.API_VERSION,
        "llm_provider": llm_provider,
    }


@router.get("/ready")
async def readiness_check():
    return {"status": "ready"}
