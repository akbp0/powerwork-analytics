"""Liveness probe. Does not touch the database, so it stays useful as a
container healthcheck even if warehouse_db is briefly unreachable."""
from __future__ import annotations

from flask_restx import Namespace, Resource

from api.models.dto import HealthDTO

health_ns = Namespace("health", description="Liveness check", path="/health")


@health_ns.route("")
class HealthResource(Resource):
    @health_ns.marshal_with(HealthDTO.status)
    @health_ns.doc(summary="Liveness probe")
    def get(self):
        return {"status": "ok"}
