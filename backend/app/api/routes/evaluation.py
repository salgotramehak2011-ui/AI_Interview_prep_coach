"""Evaluation and analytics API routes."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_analytics_service, get_interview_service
from app.schemas.evaluation_schema import AnalyticsSummary
from app.services.analytics_service import AnalyticsService
from app.services.interview_service import InterviewService
from loguru import logger

router = APIRouter(prefix="/evaluation", tags=["Evaluation"])


@router.get("/analytics/{user_id}", response_model=AnalyticsSummary)
async def get_user_analytics(
    user_id: str,
    service: AnalyticsService = Depends(get_analytics_service),
):
    try:
        return service.get_user_analytics(user_id)
    except Exception as exc:
        logger.exception("Analytics failed")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@router.get("/session/{session_id}/summary")
async def get_session_summary(
    session_id: str,
    analytics: AnalyticsService = Depends(get_analytics_service),
    interview: InterviewService = Depends(get_interview_service),
):
    session = interview.get_session(session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return analytics.get_session_analytics(session_id)
