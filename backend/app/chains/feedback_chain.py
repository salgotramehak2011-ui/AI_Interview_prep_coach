"""Improvement feedback generation chain."""

from app.llm.model_router import get_model_router
from app.prompts import get_domain_prompts
from loguru import logger


class FeedbackChain:
    """Generate domain-specific improvement feedback."""

    def __init__(self) -> None:
        self.router = get_model_router()

    async def generate_feedback(
        self,
        domain: str,
        question: str,
        answer: str,
        scores: dict,
    ) -> str:
        prompts = get_domain_prompts(domain)
        prompt = prompts.FEEDBACK_TEMPLATE.format(
            question=question,
            answer=answer,
            technical=scores.get("technical_correctness", 0),
            clarity=scores.get("communication_clarity", 0),
            confidence=scores.get("confidence", 0),
            depth=scores.get("depth_of_knowledge", 0),
        )
        logger.debug("Generating feedback for domain={}", domain)
        return await self.router.invoke(prompt, system=prompts.SYSTEM_PROMPT)
