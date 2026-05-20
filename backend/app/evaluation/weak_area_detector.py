"""Detect weak areas from evaluation results."""

from typing import Any, Dict, List

from app.core.constants import WEAK_AREA_THRESHOLD


class WeakAreaDetector:
    """Identify concepts and dimensions needing improvement."""

    def detect(
        self,
        evaluation: Dict[str, Any],
        overall_score: float,
    ) -> List[str]:
        weak: List[str] = list(evaluation.get("weak_concepts") or [])

        dimension_map = {
            "technical_correctness": "technical fundamentals",
            "communication_clarity": "communication skills",
            "confidence": "interview confidence",
            "depth_of_knowledge": "conceptual depth",
        }
        for dim, label in dimension_map.items():
            if evaluation.get(dim, 100) < WEAK_AREA_THRESHOLD:
                if label not in weak:
                    weak.append(label)

        if overall_score < WEAK_AREA_THRESHOLD and "overall performance" not in weak:
            weak.append("overall performance")

        return weak[:10]

    def priority(self, score: float) -> str:
        if score < 40:
            return "high"
        if score < 60:
            return "medium"
        return "low"
