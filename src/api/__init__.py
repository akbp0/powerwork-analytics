from __future__ import annotations

from pathlib import Path

from flask import Flask, send_from_directory

from api.extensions.db import warehouse_db
from api.extensions.restx import api, register_spec_routes
from api.namespaces.analytics import analytics_ns
from api.namespaces.health import health_ns
from config.settings import Settings


class AppFactory:
    def __init__(self, settings: Settings | None = None):
        self._settings = settings or Settings()

    def build(self) -> Flask:
        app = Flask(__name__)
        app.config.from_object(self._settings)

        self._register_extensions(app)
        self._register_api(app)
        self._register_dashboard(app)

        return app

    @staticmethod
    def _register_extensions(app: Flask) -> None:
        warehouse_db.init_app(app)

    @staticmethod
    def _register_api(app: Flask) -> None:
        api.init_app(app)
        api.add_namespace(health_ns)
        api.add_namespace(analytics_ns)
        # Register helper route that exposes the generated OpenAPI JSON
        register_spec_routes(app)

    @staticmethod
    def _register_dashboard(app: Flask) -> None:
        dashboard_dir = Path(app.root_path).parent.parent / "dashboard"

        @app.get("/")
        def dashboard():
            return send_from_directory(dashboard_dir, "index.html")


def create_app() -> Flask:
    """Entrypoint used by gunicorn (``api:create_app()``) and by tests."""
    return AppFactory().build()
