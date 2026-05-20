"""Weighted scoring engine."""

from typing import Dict

from app.core.constants import SCORE_WEIGHTS
from app.schemas.evaluation_schema import ScoreBreakdown


class ScoringEngine:
    """Compute weighted overall scores from dimension scores."""

    def compute_overall(self, scores: Dict[str, float]) -> float:
        total = 0.0
        for dimension, weight in SCORE_WEIGHTS.items():
            total += scores.get(dimension, 0.0) * weight
        return round(total, 2)

    def to_breakdown(self, raw: Dict[str, float]) -> ScoreBreakdown:
        scores = {
            "technical_correctness": raw.get("technical_correctness", 0),
            "communication_clarity": raw.get("communication_clarity", 0),
            "confidence": raw.get("confidence", 0),
            "depth_of_knowledge": raw.get("depth_of_knowledge", 0),
        }
        overall = self.compute_overall(scores)
        return ScoreBreakdown(**scores, overall_score=overall)
