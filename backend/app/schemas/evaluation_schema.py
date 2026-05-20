"""Pydantic schemas for evaluation and analytics."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class ScoreBreakdown(BaseModel):
    technical_correctness: float = Field(ge=0, le=100)
    communication_clarity: float = Field(ge=0, le=100)
    confidence: float = Field(ge=0, le=100)
    depth_of_knowledge: float = Field(ge=0, le=100)
    overall_score: float = Field(ge=0, le=100)


class EvaluationResult(BaseModel):
    question: str
    answer: str
    scores: ScoreBreakdown
    feedback: str
    weak_concepts: list[str] = Field(default_factory=list)
    evaluated_at: datetime = Field(default_factory=datetime.utcnow)


class WeakAreaRecord(BaseModel):
    id: Optional[int] = None
    user_id: str
    domain: str
    concept: str
    score: float
    occurrences: int = 1
    suggestions: list[str] = Field(default_factory=list)
    last_seen: datetime = Field(default_factory=datetime.utcnow)


class LearningRoadmapItem(BaseModel):
    concept: str
    priority: str  # high, medium, low
    resources: list[str] = Field(default_factory=list)
    estimated_weeks: int = 1


class AnalyticsSummary(BaseModel):
    user_id: str
    total_sessions: int
    average_score: float
    domain_scores: dict[str, float]
    weak_areas: list[WeakAreaRecord]
    performance_trend: list[dict[str, Any]]
    roadmap: list[LearningRoadmapItem] = Field(default_factory=list)


class SessionAnalytics(BaseModel):
    session_id: str
    domain: str
    average_score: float
    evaluations: list[EvaluationResult]
    weak_concepts: list[str]
