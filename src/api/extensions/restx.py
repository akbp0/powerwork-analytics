
from __future__ import annotations

from typing import Dict
from flask_restx import Api
from flask import jsonify, Flask

# Security schemes shown in the Swagger UI (lock icon) and added to the
# generated OpenAPI document. These give the UI a realistic "try it out"
# experience and document how clients should authenticate.
authorizations: Dict = {
    "Bearer": {
        "type": "apiKey",
        "in": "header",
        "name": "Authorization",
        "description": "JWT auth using: 'Authorization: Bearer <token>'",
    },
    "X-API-Key": {
        "type": "apiKey",
        "in": "header",
        "name": "X-API-Key",
        "description": "Optional header for service-to-service calls",
    },
}

api = Api(
    title="PowerWork Analytics API",
    version="1.0.0",
    description=(
        "Read-only analytical REST API over the PowerWork warehouse "
        "(mart star schema). See docs/architecture/README.md and "
        "docs/data-model/README.md in the repository for the pipeline "
        "and schema this API sits on top of."
    ),
    doc="/api/docs/",
    prefix="/api",
    authorizations=authorizations,
    security="Bearer",
)


@api.errorhandler
def handle_unexpected_error(error: Exception):
    return {"error": {"code": "internal_error", "message": str(error)}}, 500


def register_spec_routes(app: Flask) -> None:
    @app.route(f"{api.prefix}/openapi.json")
    def openapi_json():
        # api.__schema__ is the generated OpenAPI/Swagger spec as a dict.
        return jsonify(api.__schema__)
