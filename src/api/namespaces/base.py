from __future__ import annotations

from flask_restx import Resource

from api.extensions.db import warehouse_db
from api.repositories.analytics_repository import AnalyticsRepository
from api.services.analytics_service import AnalyticsService


class BaseAnalyticsResource(Resource):
    _service: AnalyticsService | None = None

    @property
    def service(self) -> AnalyticsService:
        if self._service is None:
            self._service = AnalyticsService(AnalyticsRepository(warehouse_db.get_connection()))
        return self._service
