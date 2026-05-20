"""Persistent weak area tracking."""

import json
from datetime import datetime
from typing import Any, Dict, List

from loguru import logger

from app.config import get_settings
from app.memory.session_memory import SessionMemory


class WeakAreaMemory:
    """Store and retrieve user weak areas from SQLite."""

    def __init__(self) -> None:
        self.session_memory = SessionMemory()

    @property
    def db_path(self):
        return get_settings().database_path

    def record_weak_areas(
        self,
        user_id: str,
        domain: str,
        concepts: List[str],
        score: float,
        suggestions: List[str] | None = None,
    ) -> None:
        if not concepts:
            return
        suggestions = suggestions or []
        now = datetime.utcnow().isoformat()
        with self.session_memory._connect() as conn:
            for concept in concepts:
                existing = conn.execute(
                    """
                    SELECT id, occurrences FROM weak_areas
                    WHERE user_id = ? AND domain = ? AND concept = ?
                    """,
                    (user_id, domain, concept),
                ).fetchone()
                if existing:
                    conn.execute(
                        """
                        UPDATE weak_areas
                        SET score = MIN(score, ?), occurrences = occurrences + 1,
                            suggestions = ?, last_seen = ?
                        WHERE id = ?
                        """,
                        (score, json.dumps(suggestions), now, existing["id"]),
                    )
                else:
                    conn.execute(
                        """
                        INSERT INTO weak_areas
                        (user_id, domain, concept, score, suggestions, last_seen)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (user_id, domain, concept, score, json.dumps(suggestions), now),
                    )
        logger.info("Recorded {} weak areas for user {}", len(concepts), user_id)

    def get_weak_areas(self, user_id: str, domain: str | None = None) -> List[Dict[str, Any]]:
        query = "SELECT * FROM weak_areas WHERE user_id = ?"
        params: list = [user_id]
        if domain:
            query += " AND domain = ?"
            params.append(domain)
        query += " ORDER BY score ASC, occurrences DESC"
        with self.session_memory._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        results = []
        for row in rows:
            data = dict(row)
            data["suggestions"] = json.loads(data.get("suggestions") or "[]")
            results.append(data)
        return results

    def record_score(self, user_id: str, session_id: str, domain: str, overall_score: float):
        now = datetime.utcnow().isoformat()
        with self.session_memory._connect() as conn:
            conn.execute(
                """
                INSERT INTO score_history (user_id, session_id, domain, overall_score, recorded_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (user_id, session_id, domain, overall_score, now),
            )
