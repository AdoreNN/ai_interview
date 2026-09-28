from sqlalchemy.exc import OperationalError

from app.db.session import get_db
from app.main import app


def test_health_reports_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_reports_database_failure(client):
    class BrokenSession:
        def execute(self, _):
            raise OperationalError("SELECT 1", {}, Exception("offline"))

    def broken_db():
        yield BrokenSession()

    app.dependency_overrides[get_db] = broken_db
    try:
        response = client.get("/health")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "service_unavailable"


def test_openapi_contains_only_planned_application_routes(client):
    paths = set(client.get("/openapi.json").json()["paths"])
    assert paths == {
        "/health",
        "/api/v1/auth/sign-up",
        "/api/v1/auth/sign-in",
        "/api/v1/sessions",
        "/api/v1/sessions/{session_id}",
    }

