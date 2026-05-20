"""Analytics aggregation engine."""

from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List

from app.memory.session_memory import SessionMemory
from app.memory.weak_area_memory import WeakAreaMemory
from app.schemas.evaluation_schema import AnalyticsSummary, LearningRoadmapItem, WeakAreaRecord


class AnalyticsEngine:
    """Build analytics dashboards from SQLite data."""

    def __init__(self) -> None:
        self.sessions = SessionMemory()
        self.weak_memory = WeakAreaMemory()

    def get_user_analytics(self, user_id: str) -> AnalyticsSummary:
        sessions = self.sessions.list_user_sessions(user_id)
        weak_areas_raw = self.weak_memory.get_weak_areas(user_id)

        domain_scores: Dict[str, List[float]] = defaultdict(list)
        trend: List[Dict[str, Any]] = []

        with self.sessions._connect() as conn:
            rows = conn.execute(
                """
                SELECT domain, overall_score, recorded_at
                FROM score_history WHERE user_id = ?
                ORDER BY recorded_at ASC
                """,
                (user_id,),
            ).fetchall()

        for row in rows:
            domain_scores[row["domain"]].append(row["overall_score"])
            trend.append(
                {
                    "domain": row["domain"],
                    "score": row["overall_score"],
                    "date": row["recorded_at"],
                }
            )

        avg_by_domain = {
            d: round(sum(scores) / len(scores), 2) if scores else 0.0
            for d, scores in domain_scores.items()
        }
        all_scores = [s for scores in domain_scores.values() for s in scores]
        average_score = round(sum(all_scores) / len(all_scores), 2) if all_scores else 0.0

        weak_records = [
            WeakAreaRecord(
                id=w.get("id"),
                user_id=w["user_id"],
                domain=w["domain"],
                concept=w["concept"],
                score=w["score"],
                occurrences=w["occurrences"],
                suggestions=w.get("suggestions", []),
                last_seen=datetime.fromisoformat(w["last_seen"]),
            )
            for w in weak_areas_raw
        ]

        roadmap = self._build_roadmap(weak_records)

        return AnalyticsSummary(
            user_id=user_id,
            total_sessions=len(sessions),
            average_score=average_score,
            domain_scores=avg_by_domain,
            weak_areas=weak_records,
            performance_trend=trend,
            roadmap=roadmap,
        )

    def _build_roadmap(self, weak_areas: List[WeakAreaRecord]) -> List[LearningRoadmapItem]:
        items = []
        for wa in weak_areas[:8]:
            priority = "high" if wa.score < 50 else "medium" if wa.score < 70 else "low"
            resources = wa.suggestions or [
                f"Study {wa.concept} fundamentals",
                f"Practice {wa.domain} interview questions",
            ]
            items.append(
                LearningRoadmapItem(
                    concept=wa.concept,
                    priority=priority,
                    resources=resources,
                    estimated_weeks=2 if priority == "high" else 1,
                )
            )
        return items

    def get_session_analytics(self, session_id: str) -> Dict[str, Any]:
        session = self.sessions.get_session(session_id)
        if not session:
            return {}
        evaluations = session.get("evaluations", [])
        scores = [e.get("overall_score", 0) for e in evaluations]
        avg = round(sum(scores) / len(scores), 2) if scores else 0.0
        weak = []
        for e in evaluations:
            weak.extend(e.get("weak_concepts", []))
        return {
            "session_id": session_id,
            "domain": session["domain"],
            "average_score": avg,
            "evaluations": evaluations,
            "weak_concepts": list(set(weak)),
        }
