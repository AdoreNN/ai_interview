from app.schemas.resume import ResumeParseResponse

from tests.test_sessions import VALID_SESSION, auth, register


PARSED = ResumeParseResponse.model_validate(
    {
        "parsed_resume": {
            "resume_topics": ["Python", "PostgreSQL"],
            "resume_experience": {"Python": 3},
            "target_position": "Python developer",
            "experience_level": "middle",
        },
        "github_profile": None,
        "questions": [
            {
                "topic": "Python",
                "question": "Как устроен ваш Python-сервис?",
                "target_agent": "tech",
            }
        ],
    }
)


def create_session(client, token: str) -> dict:
    response = client.post("/api/v1/sessions", json=VALID_SESSION, headers=auth(token))
    assert response.status_code == 201
    return response.json()


def test_resume_upload_is_parsed_and_persisted(client, monkeypatch):
    user = register(client, "resume@example.com")
    session = create_session(client, user["access_token"])

    async def fake_parse(*_):
        return PARSED

    monkeypatch.setattr("app.api.routes.resumes.parse_resume", fake_parse)
    response = client.post(
        f"/api/v1/sessions/{session['id']}/resume",
        headers=auth(user["access_token"]),
        files={"file": ("resume.pdf", b"%PDF fixture", "application/pdf")},
    )
    assert response.status_code == 200
    assert response.json()["parsed_resume"]["resume_topics"] == ["Python", "PostgreSQL"]

    retrieved = client.get(
        f"/api/v1/sessions/{session['id']}", headers=auth(user["access_token"])
    )
    assert retrieved.json()["has_resume"] is True


def test_resume_upload_validates_type_and_ownership(client, monkeypatch):
    owner = register(client, "resume-owner@example.com")
    outsider = register(client, "resume-outsider@example.com")
    session = create_session(client, owner["access_token"])

    wrong_type = client.post(
        f"/api/v1/sessions/{session['id']}/resume",
        headers=auth(owner["access_token"]),
        files={"file": ("resume.txt", b"text", "text/plain")},
    )
    foreign = client.post(
        f"/api/v1/sessions/{session['id']}/resume",
        headers=auth(outsider["access_token"]),
        files={"file": ("resume.pdf", b"%PDF", "application/pdf")},
    )
    assert wrong_type.status_code == 422
    assert foreign.status_code == 404
