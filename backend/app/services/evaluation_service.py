"""Evaluation orchestration service."""

from typing import Any, Dict, Optional

from app.chains.evaluation_chain import EvaluationChain
from app.chains.feedback_chain import FeedbackChain
from app.evaluation.scoring_engine import ScoringEngine
from app.evaluation.weak_area_detector import WeakAreaDetector
from app.memory.weak_area_memory import WeakAreaMemory
from app.schemas.interview_schema import AnswerEvaluationDetail
from loguru import logger


class EvaluationService:
    """Evaluate answers and persist weak areas."""

    def __init__(self) -> None:
        self.eval_chain = EvaluationChain()
        self.feedback_chain = FeedbackChain()
        self.scoring = ScoringEngine()
        self.weak_detector = WeakAreaDetector()
        self.weak_memory = WeakAreaMemory()

    async def evaluate_answer(
        self,
        user_id: str,
        session_id: str,
        domain: str,
        difficulty: str,
        question: str,
        answer: str,
        context: str = "",
        voice_metrics: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        raw = await self.eval_chain.evaluate(
            domain=domain,
            difficulty=difficulty,
            question=question,
            answer=answer,
            context=context,
            voice_metrics=voice_metrics,
        )
        breakdown = self.scoring.to_breakdown(raw)
        overall = breakdown.overall_score

        # Enrich feedback if LLM feedback is short
        if len(raw.get("feedback", "")) < 50:
            extra = await self.feedback_chain.generate_feedback(
                domain, question, answer, raw
            )
            raw["feedback"] = extra

        weak_concepts = self.weak_detector.detect(raw, overall)

        self.weak_memory.record_weak_areas(
            user_id=user_id,
            domain=domain,
            concepts=weak_concepts,
            score=overall,
            suggestions=[raw.get("feedback", "")],
        )
        self.weak_memory.record_score(user_id, session_id, domain, overall)

        logger.info("Evaluated answer session={} overall={}", session_id, overall)

        return {
            "technical_correctness": breakdown.technical_correctness,
            "communication_clarity": breakdown.communication_clarity,
            "confidence": breakdown.confidence,
            "depth_of_knowledge": breakdown.depth_of_knowledge,
            "overall_score": overall,
            "feedback": raw["feedback"],
            "weak_concepts": weak_concepts,
            "voice_evaluation": voice_metrics,
        }

    def to_schema(self, result: Dict[str, Any]) -> AnswerEvaluationDetail:
        return AnswerEvaluationDetail(**result)
