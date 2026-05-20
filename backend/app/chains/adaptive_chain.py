"""Adaptive follow-up and next-question chain."""

from app.chains.question_chain import QuestionChain
from app.llm.model_router import get_model_router
from app.prompts import get_domain_prompts
from loguru import logger


class AdaptiveChain:
    """Generate follow-up questions based on answer quality."""

    def __init__(self) -> None:
        self.router = get_model_router()
        self.question_chain = QuestionChain()

    async def generate_follow_up(
        self,
        domain: str,
        question: str,
        answer: str,
        evaluation_summary: str,
    ) -> str:
        prompts = get_domain_prompts(domain)
        prompt = prompts.FOLLOW_UP_TEMPLATE.format(
            question=question,
            answer=answer,
            evaluation=evaluation_summary,
        )
        logger.info("Generating follow-up for domain={}", domain)
        follow_up = await self.router.invoke(prompt, system=prompts.SYSTEM_PROMPT)
        return follow_up.strip()

    async def should_ask_follow_up(self, overall_score: float, difficulty: str) -> bool:
        """Ask follow-up when score is below threshold (stricter for advanced)."""
        thresholds = {"beginner": 75, "intermediate": 70, "advanced": 65}
        threshold = thresholds.get(difficulty, 70)
        return overall_score < threshold

    async def generate_next_question(
        self,
        domain: str,
        difficulty: str,
        context: str,
        chat_history: list,
    ) -> str:
        return await self.question_chain.generate_question(
            domain, difficulty, context, chat_history
        )
