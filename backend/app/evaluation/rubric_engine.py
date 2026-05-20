"""Interview evaluation rubric definitions."""

from typing import Dict, List


class RubricEngine:
    """Domain-agnostic rubric criteria for scoring guidance."""

    DIMENSIONS = [
        "technical_correctness",
        "communication_clarity",
        "confidence",
        "depth_of_knowledge",
    ]

    CRITERIA: Dict[str, List[str]] = {
        "technical_correctness": [
            "Accuracy of technical facts",
            "Correct use of terminology",
            "Appropriate examples and edge cases",
        ],
        "communication_clarity": [
            "Logical structure of answer",
            "Clear and concise explanation",
            "Appropriate level of detail",
        ],
        "confidence": [
            "Decisiveness without overconfidence",
            "Acknowledgment of uncertainty when appropriate",
            "Professional tone",
        ],
        "depth_of_knowledge": [
            "Beyond surface-level understanding",
            "Connections between concepts",
            "Real-world application awareness",
        ],
    }

    def get_rubric_text(self) -> str:
        lines = []
        for dim, criteria in self.CRITERIA.items():
            lines.append(f"{dim}:")
            for c in criteria:
                lines.append(f"  - {c}")
        return "\n".join(lines)
