"""General helper utilities."""

import json
import uuid
from datetime import datetime
from typing import Any


def generate_session_id() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.utcnow()


def safe_json_loads(text: str, default: Any = None) -> Any:
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return default


def truncate_text(text: str, max_len: int = 500) -> str:
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."
