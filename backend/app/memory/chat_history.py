"""Chat history formatting for LLM context."""

from typing import Any, Dict, List


class ChatHistoryFormatter:
    """Format session messages for prompt injection."""

    @staticmethod
    def format_history(messages: List[Dict[str, Any]], max_turns: int = 10) -> str:
        if not messages:
            return "No previous questions in this session."
        recent = messages[-max_turns:]
        lines = []
        for msg in recent:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            lines.append(f"{role.upper()}: {content}")
        return "\n".join(lines)

    @staticmethod
    def append_message(
        messages: List[Dict[str, Any]],
        role: str,
        content: str,
        metadata: Dict[str, Any] | None = None,
    ) -> List[Dict[str, Any]]:
        entry = {"role": role, "content": content}
        if metadata:
            entry["metadata"] = metadata
        messages.append(entry)
        return messages
