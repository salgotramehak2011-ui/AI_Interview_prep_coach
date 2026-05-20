"""Text cleaning utilities for RAG and LLM pipelines."""

import re
import unicodedata


def normalize_whitespace(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def clean_pdf_text(text: str) -> str:
    """Remove common PDF artifacts."""
    text = re.sub(r"\x0c", "\n", text)  # form feeds
    text = re.sub(r"-\n", "", text)  # hyphenation
    text = re.sub(r"\n{3,}", "\n\n", text)
    return normalize_whitespace(text)


def strip_markdown_fences(text: str) -> str:
    text = re.sub(r"^```(?:json)?\s*", "", text.strip())
    text = re.sub(r"\s*```$", "", text)
    return text.strip()
