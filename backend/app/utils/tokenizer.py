"""Simple token estimation for context window management."""

import re


def estimate_tokens(text: str) -> int:
    """Rough token count (~4 chars per token for English)."""
    if not text:
        return 0
    words = re.findall(r"\S+", text)
    return max(1, int(len(words) * 1.3))


def truncate_to_tokens(text: str, max_tokens: int) -> str:
    words = text.split()
    approx_words = int(max_tokens / 1.3)
    if len(words) <= approx_words:
        return text
    return " ".join(words[:approx_words]) + "..."
