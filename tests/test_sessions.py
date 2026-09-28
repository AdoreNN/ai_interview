import uuid



def register(client, email: str) -> dict:
    response = client.post(
        "/api/v1/auth/sign-up", json={"email": email, "password": "secure-password"}
    )
    assert response.status_code == 201
    return response.json()


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


VALID_SESSION = {
    "title": "Python Junior",
    "target_position": "Python developer",
    "experience_level": "junior",
}


def test_create_session_trims_values_and_sets_owner(client):
    user = register(client, "owner@example.com")
    response = client.post(
        "/api/v1/sessions",
        json={**VALID_SESSION, "title": "  Python Junior  ", "target_position": " Python developer "},
        headers=auth(user["access_token"]),
    )
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Python Junior"
    assert body["target_position"] == "Python developer"
    assert body["status"] == "created"


def test_create_session_validates_configuration(client):
    user = register(client, "owner@example.com")
    headers = auth(user["access_token"])
    payloads = [
        {**VALID_SESSION, "title": " "},
        {**VALID_SESSION, "title": "x" * 121},
        {**VALID_SESSION, "target_position": " "},
        {**VALID_SESSION, "experience_level": "lead"},
    ]
    for payload in payloads:
        assert client.post("/api/v1/sessions", json=payload, headers=headers).status_code == 422


def test_list_returns_only_current_users_sessions_newest_first(client):
    first_user = register(client, "first@example.com")
    second_user = register(client, "second@example.com")
    first_headers = auth(first_user["access_token"])

    first = client.post(
        "/api/v1/sessions", json={**VALID_SESSION, "title": "First"}, headers=first_headers
    ).json()
    second = client.post(
        "/api/v1/sessions", json={**VALID_SESSION, "title": "Second"}, headers=first_headers
    ).json()
    client.post(
        "/api/v1/sessions",
        json={**VALID_SESSION, "title": "Foreign"},
        headers=auth(second_user["access_token"]),
    )

    response = client.get("/api/v1/sessions", headers=first_headers)
    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [second["id"], first["id"]]


def test_empty_session_list(client):
    user = register(client, "empty@example.com")
    response = client.get("/api/v1/sessions", headers=auth(user["access_token"]))
    assert response.status_code == 200
    assert response.json() == []


def test_get_session_enforces_ownership(client):
    owner = register(client, "owner@example.com")
    outsider = register(client, "outsider@example.com")
    created = client.post(
        "/api/v1/sessions", json=VALID_SESSION, headers=auth(owner["access_token"])
    ).json()

    owned = client.get(
        f"/api/v1/sessions/{created['id']}", headers=auth(owner["access_token"])
    )
    foreign = client.get(
        f"/api/v1/sessions/{created['id']}", headers=auth(outsider["access_token"])
    )
    unknown = client.get(
        f"/api/v1/sessions/{uuid.uuid4()}", headers=auth(outsider["access_token"])
    )
    assert owned.status_code == 200
    assert foreign.status_code == unknown.status_code == 404
    assert foreign.json() == unknown.json()

