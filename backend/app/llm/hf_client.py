"""Hugging Face Inference API client for LLM completions."""

from typing import Any, Dict, List, Optional
import httpx
from loguru import logger

from app.config import get_settings


class HFClient:
    """Client for Hugging Face serverless Inference API (OpenAI-compatible)."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.api_key = self.settings.HF_TOKEN
        self.model_id = self.settings.HF_MODEL_ID
        self.base_url = self.settings.HF_API_BASE_URL.rstrip("/")
        self.timeout = self.settings.LLM_TIMEOUT

    def is_configured(self) -> bool:
        """Check if Hugging Face token is provided."""
        return bool(self.api_key)

    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate a response using Hugging Face chat completion endpoint."""
        if not self.is_configured():
            raise ValueError("Hugging Face HF_TOKEN is not configured.")

        messages: List[Dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model_id,
            "messages": messages,
            "temperature": temperature if temperature is not None else self.settings.LLM_TEMPERATURE,
            "stream": False,
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        url = f"{self.base_url}/chat/completions"
        logger.info("Calling Hugging Face Inference API: {} model={}", url, self.model_id)

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    url,
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                return content.strip()
            except Exception as exc:
                logger.error("Hugging Face generate failed for model {}: {}", self.model_id, exc)
                raise
