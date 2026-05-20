"""Ollama HTTP client for local LLM inference."""

from typing import Any, Dict, List, Optional

import httpx
from loguru import logger

from app.config import get_settings


class OllamaClient:
    """Low-level Ollama API client."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.base_url = self.settings.OLLAMA_BASE_URL.rstrip("/")
        self.timeout = self.settings.LLM_TIMEOUT

    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        system: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> str:
        model = model or self.settings.OLLAMA_PRIMARY_MODEL
        temperature = temperature if temperature is not None else self.settings.LLM_TEMPERATURE

        messages: List[Dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature},
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                return data.get("message", {}).get("content", "").strip()
            except Exception as exc:
                logger.error("Ollama generate failed for model {}: {}", model, exc)
                raise

    async def is_model_available(self, model: str) -> bool:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
                available_models = []
                for m in response.json().get("models", []):
                    name = m.get("name", "")
                    available_models.append(name)
                    available_models.append(name.split(":")[0])
                return model in available_models
        except Exception:
            return False
