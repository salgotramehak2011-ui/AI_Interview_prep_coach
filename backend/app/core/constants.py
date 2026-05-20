"""Application-wide constants."""

from enum import Enum


class Domain(str, Enum):
    AI_ML = "ai_ml"
    WEB_DEV = "web_dev"
    CYBERSECURITY = "cybersecurity"


class Difficulty(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


DOMAIN_LABELS = {
    Domain.AI_ML: "AI / Machine Learning",
    Domain.WEB_DEV: "Web Development",
    Domain.CYBERSECURITY: "Cybersecurity",
}

VALID_DOMAINS = [d.value for d in Domain]
VALID_DIFFICULTIES = [d.value for d in Difficulty]

# Scoring weights (sum = 1.0)
SCORE_WEIGHTS = {
    "technical_correctness": 0.35,
    "communication_clarity": 0.25,
    "confidence": 0.20,
    "depth_of_knowledge": 0.20,
}

WEAK_AREA_THRESHOLD = 60.0  # Below this overall score marks a weak area

CHROMA_COLLECTION_PREFIX = "interview_"
