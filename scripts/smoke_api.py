import json
from io import BytesIO
import os
import time
import urllib.error
import urllib.request
import uuid

import httpx
from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject


BASE_URL = os.environ.get("SMOKE_BASE_URL", "http://127.0.0.1:8000")
PARSER_URL = os.environ.get("SMOKE_PARSER_URL", "http://127.0.0.1:8001")


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


def wait_for_parser() -> None:
    for _ in range(30):
        try:
            with urllib.request.urlopen(PARSER_URL + "/health", timeout=10) as response:
                body = json.loads(response.read().decode())
                if response.status == 200 and body["status"] == "ok":
                    return
        except (OSError, urllib.error.URLError):
            time.sleep(1)
    raise SystemExit("resume parser did not become healthy")


def resume_pdf() -> bytes:
    output = BytesIO()
    writer = PdfWriter()
    page = writer.add_blank_page(width=612, height=792)
    font = DictionaryObject(
        {
            NameObject("/Type"): NameObject("/Font"),
            NameObject("/Subtype"): NameObject("/Type1"),
            NameObject("/BaseFont"): NameObject("/Helvetica"),
        }
    )
    page[NameObject("/Resources")] = DictionaryObject(
        {NameObject("/Font"): DictionaryObject({NameObject("/F1"): font})}
    )
    stream = DecodedStreamObject()
    stream.set_data(b"BT /F1 12 Tf 72 720 Td (Python backend developer) Tj ET")
    page[NameObject("/Contents")] = writer._add_object(stream)
    writer.write(output)
    return output.getvalue()


def main() -> None:
    wait_for_health()
    wait_for_parser()
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

    parsed = httpx.post(
        f"{BASE_URL}/api/v1/sessions/{created['id']}/resume",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("resume.pdf", resume_pdf(), "application/pdf")},
        timeout=45,
    )
    assert parsed.status_code == 200, parsed.text
    assert parsed.json()["parsed_resume"]["resume_topics"] == ["Python"]

    status, turn = request(
        "POST", f"/api/v1/sessions/{created['id']}/interview/start", {}, token
    )
    assert status == 200 and turn["status"] == "in_progress" and turn["current_question"]
    for _ in range(10):
        status, turn = request(
            "POST",
            f"/api/v1/sessions/{created['id']}/interview/answer",
            {"answer": "Конкретный ответ кандидата с примером из проекта."},
            token,
        )
        assert status == 200
        if turn["status"] == "completed":
            break
    assert turn["status"] == "completed" and turn["final_feedback"]


if __name__ == "__main__":
    main()
