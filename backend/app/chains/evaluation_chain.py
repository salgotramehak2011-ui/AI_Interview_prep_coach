"""Answer evaluation chain using LLM + rubric."""

from typing import Any, Dict, Optional

from app.llm.model_router import get_model_router
from app.prompts import evaluation_prompt
from app.utils.cleaner import strip_markdown_fences
from app.utils.helper import safe_json_loads
from loguru import logger


class EvaluationChain:
    """Evaluate interview answers via structured LLM output."""

    def __init__(self) -> None:
        self.router = get_model_router()

    async def evaluate(
        self,
        domain: str,
        difficulty: str,
        question: str,
        answer: str,
        context: str = "",
        voice_metrics: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        voice_info = ""
        if voice_metrics:
            filler_words = ", ".join(voice_metrics.get("filler_words_detected", [])) or "none"
            voice_info = f"""
Optional voice metrics (speech dynamics) of the candidate's speech:
- Speaking Duration: {voice_metrics.get('speaking_duration', 0.0):.1f} seconds
- Words Per Minute: {voice_metrics.get('words_per_minute', 0.0):.1f} WPM
- Filler Words Count: {voice_metrics.get('filler_word_count', 0)} (detected: {filler_words})
- Speech Clarity / Confidence Score: {voice_metrics.get('speech_clarity_score', 0.0):.1f}%

Factor these speech dynamics into your overall scores (especially lowering 'communication_clarity' or 'confidence' if there are high filler word counts or very low clarity/confidence scores, and highlighting them in your feedback).
"""

        prompt = evaluation_prompt.EVALUATION_TEMPLATE.format(
            domain=domain,
            difficulty=difficulty,
            question=question,
            answer=answer,
            context=context or "N/A",
            voice_info=voice_info,
        )
        raw = await self.router.invoke(prompt, system=evaluation_prompt.SYSTEM_PROMPT)
        cleaned = strip_markdown_fences(raw)
        result = safe_json_loads(cleaned)
        if not result or not isinstance(result, dict):
            logger.warning("Failed to parse evaluation JSON, using defaults")
            result = self._default_evaluation(answer)
        return self._normalize_scores(result)

    def _default_evaluation(self, answer: str) -> Dict[str, Any]:
        length_score = min(100, len(answer.split()) * 3)
        return {
            "technical_correctness": length_score,
            "communication_clarity": length_score,
            "confidence": length_score,
            "depth_of_knowledge": length_score,
            "feedback": "Unable to parse detailed evaluation. Please provide more structured answers.",
            "weak_concepts": ["general knowledge"],
        }

    def _normalize_scores(self, result: Dict[str, Any]) -> Dict[str, Any]:
        for key in [
            "technical_correctness",
            "communication_clarity",
            "confidence",
            "depth_of_knowledge",
        ]:
            val = float(result.get(key, 50))
            result[key] = max(0.0, min(100.0, val))
        result["weak_concepts"] = result.get("weak_concepts") or []
        if isinstance(result["weak_concepts"], str):
            result["weak_concepts"] = [result["weak_concepts"]]
        result["feedback"] = result.get("feedback", "No feedback provided.")
        return result
