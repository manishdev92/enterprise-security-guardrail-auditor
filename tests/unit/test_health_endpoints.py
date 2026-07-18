from fastapi.testclient import TestClient

from app.main import create_app


def test_health_endpoint_returns_ok_status() -> None:
    app = create_app()
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready_endpoint_returns_ready_status() -> None:
    app = create_app()
    client = TestClient(app)

    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_root_endpoint_returns_service_information() -> None:
    app = create_app()
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    payload = response.json()
    assert payload["name"] == "Enterprise Security Guardrail Auditor"
    assert payload["status"] == "ok"
