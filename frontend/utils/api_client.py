"""HTTP client for FastAPI backend."""

import os
from typing import Any, Dict, Optional

import httpx
import streamlit as st

DEFAULT_API_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")


class APIClient:
    """REST client for interview coach backend."""

    def __init__(self, base_url: str = DEFAULT_API_URL, timeout: float = 120.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def health(self) -> Dict[str, Any]:
        with httpx.Client(timeout=10) as client:
            r = client.get(self._url("/health"))
            r.raise_for_status()
            return r.json()

    def start_interview(
        self,
        user_id: str,
        domain: str,
        difficulty: str,
        num_questions: int = 5,
    ) -> Dict[str, Any]:
        payload = {
            "user_id": user_id,
            "domain": domain,
            "difficulty": difficulty,
            "num_questions": num_questions,
        }
        with httpx.Client(timeout=self.timeout) as client:
            r = client.post(self._url("/interview/start"), json=payload)
            r.raise_for_status()
            return r.json()

    def submit_answer(
        self,
        session_id: str,
        answer: str,
        voice_metrics: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        payload = {"session_id": session_id, "answer": answer}
        if voice_metrics:
            payload["voice_metrics"] = voice_metrics
        with httpx.Client(timeout=self.timeout) as client:
            r = client.post(self._url("/interview/answer"), json=payload)
            r.raise_for_status()
            return r.json()

    def get_session(self, session_id: str) -> Dict[str, Any]:
        with httpx.Client(timeout=30) as client:
            r = client.get(self._url(f"/interview/session/{session_id}"))
            r.raise_for_status()
            return r.json()

    def get_analytics(self, user_id: str) -> Dict[str, Any]:
        with httpx.Client(timeout=30) as client:
            r = client.get(self._url(f"/evaluation/analytics/{user_id}"))
            r.raise_for_status()
            return r.json()

    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        with httpx.Client(timeout=30) as client:
            r = client.get(self._url(f"/evaluation/session/{session_id}/summary"))
            r.raise_for_status()
            return r.json()

    def ingest_domain(self, domain: str, force_rebuild: bool = False) -> Dict[str, Any]:
        with httpx.Client(timeout=300) as client:
            r = client.post(
                self._url("/rag/ingest"),
                json={"domain": domain, "force_rebuild": force_rebuild},
            )
            r.raise_for_status()
            return r.json()


def get_api_client() -> APIClient:
    api_url = st.session_state.get("api_base_url", DEFAULT_API_URL)
    return APIClient(base_url=api_url)
