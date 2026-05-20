"""Pydantic schemas for interview API."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator

from app.core.constants import VALID_DIFFICULTIES, VALID_DOMAINS


class InterviewStartRequest(BaseModel):
    user_id: str = Field(default="default_user", min_length=1)
    domain: str
    difficulty: str = "intermediate"
    num_questions: int = Field(default=5, ge=1, le=20)

    @field_validator("domain")
    @classmethod
    def validate_domain(cls, v: str) -> str:
        if v not in VALID_DOMAINS:
            raise ValueError(f"domain must be one of {VALID_DOMAINS}")
        return v

    @field_validator("difficulty")
    @classmethod
    def validate_difficulty(cls, v: str) -> str:
        if v not in VALID_DIFFICULTIES:
            raise ValueError(f"difficulty must be one of {VALID_DIFFICULTIES}")
        return v


class InterviewStartResponse(BaseModel):
    session_id: str
    domain: str
    difficulty: str
    first_question: str
    context_used: Optional[str] = None


class VoiceMetrics(BaseModel):
    speaking_duration: float
    words_per_minute: float
    filler_word_count: int
    filler_words_detected: list[str] = Field(default_factory=list)
    speech_clarity_score: float


class AnswerSubmitRequest(BaseModel):
    session_id: str
    answer: str = Field(min_length=1)
    voice_metrics: Optional[VoiceMetrics] = None


class AnswerEvaluationDetail(BaseModel):
    technical_correctness: float
    communication_clarity: float
    confidence: float
    depth_of_knowledge: float
    overall_score: float
    feedback: str
    weak_concepts: list[str] = Field(default_factory=list)
    voice_evaluation: Optional[dict[str, Any]] = None


class AnswerSubmitResponse(BaseModel):
    session_id: str
    evaluation: AnswerEvaluationDetail
    follow_up_question: Optional[str] = None
    next_question: Optional[str] = None
    is_complete: bool = False
    question_index: int = 0


class InterviewSessionResponse(BaseModel):
    session_id: str
    user_id: str
    domain: str
    difficulty: str
    status: str
    question_count: int
    current_index: int
    chat_history: list[dict[str, Any]] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class FollowUpRequest(BaseModel):
    session_id: str
    last_answer: str
