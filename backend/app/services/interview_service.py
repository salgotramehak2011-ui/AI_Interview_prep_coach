"""Interview session orchestration service."""

from typing import Any, Dict, Optional

from loguru import logger

from app.chains.adaptive_chain import AdaptiveChain
from app.chains.question_chain import QuestionChain
from app.memory.session_memory import SessionMemory
from app.schemas.interview_schema import (
    AnswerSubmitResponse,
    InterviewStartResponse,
)
from app.services.evaluation_service import EvaluationService
from app.services.rag_service import RAGService


class InterviewService:
    """Manage full interview lifecycle."""

    def __init__(self) -> None:
        self.sessions = SessionMemory()
        self.rag = RAGService()
        self.evaluation = EvaluationService()
        self.question_chain = QuestionChain()
        self.adaptive = AdaptiveChain()

    async def start_interview(
        self,
        user_id: str,
        domain: str,
        difficulty: str,
        num_questions: int = 5,
    ) -> InterviewStartResponse:
        session = self.sessions.create_session(
            user_id=user_id,
            domain=domain,
            difficulty=difficulty,
            num_questions=num_questions,
        )
        session_id = session["session_id"]

        context = self.rag.get_context(
            domain,
            f"{domain} interview questions {difficulty} level",
        )
        question = await self.question_chain.generate_question(
            domain=domain,
            difficulty=difficulty,
            context=context,
            chat_history=[],
        )

        self.sessions.add_message(session_id, "interviewer", question)
        logger.info("Started interview session={} domain={}", session_id, domain)

        return InterviewStartResponse(
            session_id=session_id,
            domain=domain,
            difficulty=difficulty,
            first_question=question,
            context_used=context[:500] if context else None,
        )

    async def submit_answer(
        self,
        session_id: str,
        answer: str,
        voice_metrics: Optional[Any] = None,
    ) -> AnswerSubmitResponse:
        session = self.sessions.get_session(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        if session["status"] == "completed":
            raise ValueError("Interview session already completed")

        history = session["chat_history"]
        # Last interviewer message is the current question
        current_question = self._get_last_interviewer_question(history)
        if not current_question:
            raise ValueError("No active question in session")

        self.sessions.add_message(
            session_id,
            "candidate",
            answer,
            metadata=voice_metrics.model_dump() if voice_metrics else None,
        )

        domain = session["domain"]
        difficulty = session["difficulty"]
        context = self.rag.get_context(domain, current_question)

        eval_result = await self.evaluation.evaluate_answer(
            user_id=session["user_id"],
            session_id=session_id,
            domain=domain,
            difficulty=difficulty,
            question=current_question,
            answer=answer,
            context=context,
            voice_metrics=voice_metrics.model_dump() if voice_metrics else None,
        )

        eval_record = {
            "question": current_question,
            "answer": answer,
            **eval_result,
        }
        self.sessions.add_evaluation(session_id, eval_record)

        current_index = session["current_index"] + 1
        self.sessions.update_session(session_id, current_index=current_index)

        follow_up: Optional[str] = None
        next_question: Optional[str] = None
        is_complete = current_index >= session["num_questions"]

        if not is_complete:
            ask_follow_up = await self.adaptive.should_ask_follow_up(
                eval_result["overall_score"], difficulty
            )
            if ask_follow_up:
                follow_up = await self.adaptive.generate_follow_up(
                    domain=domain,
                    question=current_question,
                    answer=answer,
                    evaluation_summary=eval_result["feedback"],
                )
                self.sessions.add_message(session_id, "interviewer", follow_up)
            else:
                updated = self.sessions.get_session(session_id)
                context = self.rag.get_context(
                    domain, f"interview question {difficulty}"
                )
                next_question = await self.adaptive.generate_next_question(
                    domain=domain,
                    difficulty=difficulty,
                    context=context,
                    chat_history=updated["chat_history"],
                )
                self.sessions.add_message(session_id, "interviewer", next_question)
        else:
            self.sessions.update_session(session_id, status="completed")

        from app.schemas.interview_schema import AnswerEvaluationDetail

        return AnswerSubmitResponse(
            session_id=session_id,
            evaluation=AnswerEvaluationDetail(**eval_result),
            follow_up_question=follow_up,
            next_question=next_question,
            is_complete=is_complete,
            question_index=current_index,
        )

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        return self.sessions.get_session(session_id)

    @staticmethod
    def _get_last_interviewer_question(history: list) -> Optional[str]:
        for msg in reversed(history):
            if msg.get("role") == "interviewer":
                return msg.get("content")
        return None
