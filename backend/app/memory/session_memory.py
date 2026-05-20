"""In-memory and SQLite-backed session state."""

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional

from loguru import logger

from app.config import get_settings
from app.memory.chat_history import ChatHistoryFormatter
from app.utils.helper import generate_session_id, utc_now


class SessionMemory:
    """Persist interview sessions in SQLite."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.db_path = self.settings.database_path
        self._init_db()
        self.formatter = ChatHistoryFormatter()

    @contextmanager
    def _connect(self):
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    domain TEXT NOT NULL,
                    difficulty TEXT NOT NULL,
                    status TEXT DEFAULT 'active',
                    num_questions INTEGER DEFAULT 5,
                    current_index INTEGER DEFAULT 0,
                    chat_history TEXT DEFAULT '[]',
                    evaluations TEXT DEFAULT '[]',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS weak_areas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    domain TEXT NOT NULL,
                    concept TEXT NOT NULL,
                    score REAL NOT NULL,
                    occurrences INTEGER DEFAULT 1,
                    suggestions TEXT DEFAULT '[]',
                    last_seen TEXT NOT NULL,
                    UNIQUE(user_id, domain, concept)
                );
                CREATE TABLE IF NOT EXISTS score_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    domain TEXT NOT NULL,
                    overall_score REAL NOT NULL,
                    recorded_at TEXT NOT NULL
                );
                """
            )
        logger.debug("SQLite initialized at {}", self.db_path)

    def create_session(
        self,
        user_id: str,
        domain: str,
        difficulty: str,
        num_questions: int = 5,
    ) -> Dict[str, Any]:
        session_id = generate_session_id()
        now = utc_now().isoformat()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO sessions
                (session_id, user_id, domain, difficulty, num_questions,
                 current_index, chat_history, evaluations, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, 0, '[]', '[]', ?, ?)
                """,
                (session_id, user_id, domain, difficulty, num_questions, now, now),
            )
        return self.get_session(session_id)

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM sessions WHERE session_id = ?", (session_id,)
            ).fetchone()
        if not row:
            return None
        return self._row_to_dict(row)

    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        data = dict(row)
        data["chat_history"] = json.loads(data.get("chat_history") or "[]")
        data["evaluations"] = json.loads(data.get("evaluations") or "[]")
        return data

    def update_session(self, session_id: str, **kwargs: Any) -> Optional[Dict[str, Any]]:
        session = self.get_session(session_id)
        if not session:
            return None
        allowed = {"status", "current_index", "chat_history", "evaluations", "difficulty"}
        updates = {k: v for k, v in kwargs.items() if k in allowed}
        if not updates:
            return session
        if "chat_history" in updates and isinstance(updates["chat_history"], list):
            updates["chat_history"] = json.dumps(updates["chat_history"])
        if "evaluations" in updates and isinstance(updates["evaluations"], list):
            updates["evaluations"] = json.dumps(updates["evaluations"])
        updates["updated_at"] = utc_now().isoformat()
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        values = list(updates.values()) + [session_id]
        with self._connect() as conn:
            conn.execute(f"UPDATE sessions SET {set_clause} WHERE session_id = ?", values)
        return self.get_session(session_id)

    def add_message(self, session_id: str, role: str, content: str, metadata: dict | None = None):
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        history = self.formatter.append_message(session["chat_history"], role, content, metadata)
        return self.update_session(session_id, chat_history=history)

    def add_evaluation(self, session_id: str, evaluation: Dict[str, Any]):
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        evaluations = session["evaluations"] + [evaluation]
        return self.update_session(session_id, evaluations=evaluations)

    def list_user_sessions(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM sessions WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
                (user_id, limit),
            ).fetchall()
        return [self._row_to_dict(r) for r in rows]
