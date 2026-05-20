"""Interview service unit tests."""

import pytest

from app.memory.session_memory import SessionMemory
from app.schemas.interview_schema import InterviewStartRequest


def test_interview_start_request_validation():
    req = InterviewStartRequest(user_id="u1", domain="ai_ml", difficulty="beginner")
    assert req.domain == "ai_ml"


def test_session_memory_create():
    memory = SessionMemory()
    session = memory.create_session("test_user", "web_dev", "intermediate", 3)
    assert session["session_id"]
    assert session["domain"] == "web_dev"
    fetched = memory.get_session(session["session_id"])
    assert fetched is not None
