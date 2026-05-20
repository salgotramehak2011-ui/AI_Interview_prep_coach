"""Evaluation engine unit tests."""

from app.evaluation.scoring_engine import ScoringEngine
from app.evaluation.weak_area_detector import WeakAreaDetector


def test_scoring_engine_overall():
    engine = ScoringEngine()
    scores = {
        "technical_correctness": 80,
        "communication_clarity": 70,
        "confidence": 75,
        "depth_of_knowledge": 85,
    }
    overall = engine.compute_overall(scores)
    assert 70 <= overall <= 85


def test_weak_area_detector():
    detector = WeakAreaDetector()
    evaluation = {
        "technical_correctness": 45,
        "communication_clarity": 80,
        "confidence": 70,
        "depth_of_knowledge": 55,
        "weak_concepts": ["gradient descent"],
    }
    weak = detector.detect(evaluation, 55.0)
    assert "gradient descent" in weak
