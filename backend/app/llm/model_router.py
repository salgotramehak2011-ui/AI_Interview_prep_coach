"""Route LLM requests to appropriate model with fallback."""

from functools import lru_cache
from typing import Optional

from app.llm.hf_client import HFClient
from app.llm.mistral_client import MistralClient
from loguru import logger


class ModelRouter:
    """Unified LLM entry point for all chains."""

    def __init__(self) -> None:
        self.hf_client = HFClient()
        self.ollama_client = MistralClient()

    async def invoke(self, prompt: str, system: Optional[str] = None) -> str:
        logger.debug("LLM invoke prompt length={}", len(prompt))
        
        # 1. Try Hugging Face first if token is configured
        if self.hf_client.is_configured():
            try:
                logger.info("Attempting inference via Hugging Face...")
                return await self.hf_client.generate(prompt, system=system)
            except Exception as exc:
                logger.warning("Hugging Face inference failed: {}. Falling back to Ollama...", exc)
        else:
            logger.info("Hugging Face token not configured. Using local Ollama as primary.")

        # 2. Fallback to Ollama client (which handles its own primary/fallback Ollama models)
        return await self.ollama_client.complete_with_fallback(prompt, system=system)


@lru_cache
def get_model_router() -> ModelRouter:
    return ModelRouter()
