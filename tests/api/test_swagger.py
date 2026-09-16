from api import create_app

# flask-restx puts the Api's `prefix` (here "/api", set on the Api object in
# api.extensions.restx) into the generated spec's top-level "basePath" — the
# per-path keys under spec["paths"] are relative to that basePath, not full
# absolute URLs. So these must NOT repeat the "/api" prefix.
EXPECTED_PATHS = {
    "/analytics/filters",
    "/analytics/kpis",
    "/analytics/trend",
    "/analytics/categories/breakdown",
    "/analytics/status/funnel",
    "/analytics/cities/ranking",
    "/analytics/work-orders",
    "/analytics/data-quality/reconciliation",
    "/health",
}


def test_swagger_json_lists_every_endpoint():
    app = create_app()
    client = app.test_client()

    response = client.get("/api/swagger.json")

    assert response.status_code == 200
    spec = response.json
    assert EXPECTED_PATHS.issubset(set(spec["paths"].keys()))


def test_docs_page_renders():
    app = create_app()
    client = app.test_client()

    response = client.get("/api/docs/")

    assert response.status_code == 200