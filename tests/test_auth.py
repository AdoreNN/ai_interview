import uuid

from app.core.security import create_access_token


def sign_up(client, email: str = "user@example.com", password: str = "secure-password"):
    return client.post("/api/v1/auth/sign-up", json={"email": email, "password": password})


def test_sign_up_returns_user_and_token_without_hash(client):
    response = sign_up(client, "User@Example.com")
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "user@example.com"
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert "password" not in body


def test_duplicate_email_is_case_insensitive(client):
    assert sign_up(client, "user@example.com").status_code == 201
    response = sign_up(client, "USER@example.com")
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "conflict"


def test_sign_up_validates_email_and_password(client):
    bad_email = sign_up(client, "not-an-email")
    short_password = sign_up(client, "valid@example.com", "short")
    assert bad_email.status_code == 422
    assert short_password.status_code == 422
    for response, submitted_value in ((bad_email, "not-an-email"), (short_password, "short")):
        details = response.json()["error"]["details"]
        assert all(set(detail) == {"location", "message", "type"} for detail in details)
        assert all(detail.get("input") is None for detail in details)
        assert submitted_value not in [detail.get("input") for detail in details]


def test_sign_in_success_and_generic_failures(client):
    assert sign_up(client).status_code == 201
    success = client.post(
        "/api/v1/auth/sign-in",
        json={"email": "USER@example.com", "password": "secure-password"},
    )
    unknown = client.post(
        "/api/v1/auth/sign-in",
        json={"email": "missing@example.com", "password": "secure-password"},
    )
    wrong = client.post(
        "/api/v1/auth/sign-in",
        json={"email": "user@example.com", "password": "wrong"},
    )
    assert success.status_code == 200
    assert unknown.status_code == wrong.status_code == 401
    assert unknown.json() == wrong.json()


def test_protected_route_rejects_missing_invalid_and_unknown_user_tokens(client):
    missing = client.get("/api/v1/sessions")
    invalid = client.get(
        "/api/v1/sessions", headers={"Authorization": "Bearer invalid-token"}
    )
    unknown_token = create_access_token(uuid.uuid4())
    unknown = client.get(
        "/api/v1/sessions", headers={"Authorization": f"Bearer {unknown_token}"}
    )
    assert missing.status_code == invalid.status_code == unknown.status_code == 401
