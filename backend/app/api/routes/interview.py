"""Interview API routes."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_interview_service
from app.schemas.interview_schema import (
    AnswerSubmitRequest,
    AnswerSubmitResponse,
    InterviewSessionResponse,
    InterviewStartRequest,
    InterviewStartResponse,
)
from app.services.interview_service import InterviewService
from loguru import logger

router = APIRouter(prefix="/interview", tags=["Interview"])


@router.post("/start", response_model=InterviewStartResponse)
async def start_interview(
    request: InterviewStartRequest,
    service: InterviewService = Depends(get_interview_service),
):
    try:
        return await service.start_interview(
            user_id=request.user_id,
            domain=request.domain,
            difficulty=request.difficulty,
            num_questions=request.num_questions,
        )
    except Exception as exc:
        logger.exception("Failed to start interview")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@router.post("/answer", response_model=AnswerSubmitResponse)
async def submit_answer(
    request: AnswerSubmitRequest,
    service: InterviewService = Depends(get_interview_service),
):
    try:
        return await service.submit_answer(
            session_id=request.session_id,
            answer=request.answer,
            voice_metrics=request.voice_metrics,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except Exception as exc:
        logger.exception("Failed to submit answer")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@router.get("/session/{session_id}", response_model=InterviewSessionResponse)
async def get_session(
    session_id: str,
    service: InterviewService = Depends(get_interview_service),
):
    session = service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    from datetime import datetime

    return InterviewSessionResponse(
        session_id=session["session_id"],
        user_id=session["user_id"],
        domain=session["domain"],
        difficulty=session["difficulty"],
        status=session["status"],
        question_count=session["num_questions"],
        current_index=session["current_index"],
        chat_history=session["chat_history"],
        created_at=datetime.fromisoformat(session["created_at"]),
        updated_at=datetime.fromisoformat(session["updated_at"]),
    )
