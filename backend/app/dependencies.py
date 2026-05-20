"""FastAPI dependency injection."""

from functools import lru_cache

from app.services.analytics_service import AnalyticsService
from app.services.evaluation_service import EvaluationService
from app.services.interview_service import InterviewService
from app.services.rag_service import RAGService


@lru_cache
def get_interview_service() -> InterviewService:
    return InterviewService()


@lru_cache
def get_rag_service() -> RAGService:
    return RAGService()


@lru_cache
def get_evaluation_service() -> EvaluationService:
    return EvaluationService()


@lru_cache
def get_analytics_service() -> AnalyticsService:
    return AnalyticsService()
