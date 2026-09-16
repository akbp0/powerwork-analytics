from api import create_app


def test_health():
    app = create_app()
    client = app.test_client()

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json["status"] == "ok"
