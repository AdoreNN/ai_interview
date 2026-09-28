import json
import os
import time
import urllib.error
import urllib.request
import uuid


BASE_URL = os.environ.get("SMOKE_BASE_URL", "http://127.0.0.1:8000")


def request(method: str, path: str, payload: dict | None = None, token: str | None = None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(BASE_URL + path, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=10) as response:
        return response.status, json.loads(response.read().decode())


def wait_for_health() -> None:
    for _ in range(30):
        try:
            status, body = request("GET", "/health")
            if status == 200 and body == {"status": "ok"}:
                return
        except (OSError, urllib.error.URLError):
            time.sleep(1)
    raise SystemExit("backend did not become healthy")


def main() -> None:
    wait_for_health()
    email = f"smoke-{uuid.uuid4()}@example.com"
    credentials = {"email": email, "password": "correct-horse-battery-staple"}

    status, registered = request("POST", "/api/v1/auth/sign-up", credentials)
    assert status == 201 and registered["email"] == email

    status, signed_in = request("POST", "/api/v1/auth/sign-in", credentials)
    assert status == 200 and signed_in["token_type"] == "bearer"
    token = signed_in["access_token"]

    session_payload = {
        "title": "Python Junior",
        "target_position": "Python developer",
        "experience_level": "junior",
    }
    status, created = request("POST", "/api/v1/sessions", session_payload, token)
    assert status == 201 and created["status"] == "created"

    status, sessions = request("GET", "/api/v1/sessions", token=token)
    assert status == 200 and any(item["id"] == created["id"] for item in sessions)

    status, retrieved = request("GET", f"/api/v1/sessions/{created['id']}", token=token)
    assert status == 200 and retrieved["title"] == session_payload["title"]


if __name__ == "__main__":
    main()

