"""RAG pipeline unit tests."""

import pytest

from app.core.constants import VALID_DOMAINS
from app.rag.chunking.text_chunker import TextChunker
from app.utils.validators import is_valid_domain
from langchain_core.documents import Document


def test_valid_domains():
    assert len(VALID_DOMAINS) == 3
    assert is_valid_domain("ai_ml")
    assert not is_valid_domain("invalid")


def test_text_chunker():
    chunker = TextChunker()
    docs = [Document(page_content="A" * 2500, metadata={"source": "test"})]
    chunks = chunker.chunk_documents(docs)
    assert len(chunks) >= 2
