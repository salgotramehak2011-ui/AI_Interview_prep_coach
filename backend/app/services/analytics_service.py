"""Analytics service facade."""

from app.evaluation.analytics_engine import AnalyticsEngine
from app.schemas.evaluation_schema import AnalyticsSummary


class AnalyticsService:
    def __init__(self) -> None:
        self.engine = AnalyticsEngine()

    def get_user_analytics(self, user_id: str) -> AnalyticsSummary:
        return self.engine.get_user_analytics(user_id)

    def get_session_analytics(self, session_id: str) -> dict:
        return self.engine.get_session_analytics(session_id)
