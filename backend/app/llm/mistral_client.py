"""Mistral-specific client via Ollama."""

from typing import Optional

from app.config import get_settings
from app.llm.ollama_client import OllamaClient
from loguru import logger


class MistralClient:
    """High-level Mistral interface (runs through Ollama)."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.ollama = OllamaClient()
        self.model = self.settings.OLLAMA_PRIMARY_MODEL

    async def complete(self, prompt: str, system: Optional[str] = None) -> str:
        return await self.ollama.generate(prompt, model=self.model, system=system)

    async def complete_with_fallback(self, prompt: str, system: Optional[str] = None) -> str:
        try:
            if await self.ollama.is_model_available(self.model):
                return await self.complete(prompt, system=system)
        except Exception as exc:
            logger.warning("Primary model {} failed: {}", self.model, exc)

        fallback = self.settings.OLLAMA_FALLBACK_MODEL
        logger.info("Falling back to model: {}", fallback)
        return await self.ollama.generate(prompt, model=fallback, system=system)
