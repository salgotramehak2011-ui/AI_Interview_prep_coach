"""LangChain-style question generation chain."""

from app.llm.model_router import get_model_router
from app.memory.chat_history import ChatHistoryFormatter
from app.prompts import get_domain_prompts
from loguru import logger


class QuestionChain:
    """Generate interview questions using RAG context."""

    def __init__(self) -> None:
        self.router = get_model_router()
        self.formatter = ChatHistoryFormatter()

    async def generate_question(
        self,
        domain: str,
        difficulty: str,
        context: str,
        chat_history: list,
    ) -> str:
        prompts = get_domain_prompts(domain)
        history_str = self.formatter.format_history(chat_history)
        prompt = prompts.QUESTION_TEMPLATE.format(
            difficulty=difficulty,
            context=context or "No additional context available.",
            history=history_str,
        )
        logger.info("Generating question for domain={} difficulty={}", domain, difficulty)
        question = await self.router.invoke(prompt, system=prompts.SYSTEM_PROMPT)
        return question.strip()
