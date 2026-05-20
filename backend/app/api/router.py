"""Main API router aggregation."""

from fastapi import APIRouter

from app.api.routes import evaluation, health, interview, rag

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(interview.router)
api_router.include_router(rag.router)
api_router.include_router(evaluation.router)
