from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_status_and_version_with_request_id() -> None:
    response = client.get("/api/v1/health", headers={"X-Request-ID": "health-test-001"})

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "0.1.0"}
    assert response.headers["X-Request-ID"] == "health-test-001"


def test_unknown_route_returns_404_and_invalid_request_id_is_replaced() -> None:
    response = client.get("/api/v1/not-a-route", headers={"X-Request-ID": "not valid"})

    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}
    assert response.headers["X-Request-ID"] != "not valid"
    assert response.headers["X-Request-ID"]
