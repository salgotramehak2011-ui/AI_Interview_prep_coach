"""Input validation helpers."""

from app.core.constants import VALID_DIFFICULTIES, VALID_DOMAINS


def is_valid_domain(domain: str) -> bool:
    return domain in VALID_DOMAINS


def is_valid_difficulty(difficulty: str) -> bool:
    return difficulty in VALID_DIFFICULTIES


def validate_non_empty(value: str, field_name: str) -> str:
    if not value or not value.strip():
        raise ValueError(f"{field_name} cannot be empty")
    return value.strip()
