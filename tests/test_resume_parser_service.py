from fastapi.testclient import TestClient

from pdf_parser_agent.app.main import app
from pdf_parser_agent.app.schemas import GeneratedQuestion, ParsedResume
from pdf_parser_agent.app.skills.github_lookup import extract_github_username


def test_parser_health_and_media_type_validation():
    with TestClient(app) as client:
        assert client.get("/health").json() == {"status": "ok", "agent": "pdf_parser_agent"}
        response = client.post("/v1/parse", files={"file": ("cv.txt", b"text", "text/plain")})
    assert response.status_code == 422


def test_parser_pipeline_returns_structured_result(monkeypatch):
    parsed = ParsedResume(
        resume_topics=["Python"],
        resume_experience={"Python": 2},
        target_position="Backend developer",
        experience_level="junior",
    )

    monkeypatch.setattr(
        "pdf_parser_agent.app.main.read_resume", lambda _: (parsed, "GitHub: github.com/octocat")
    )
    monkeypatch.setattr(
        "pdf_parser_agent.app.main.fetch_github_profile", lambda _: async_none()
    )
    monkeypatch.setattr(
        "pdf_parser_agent.app.main.generate_questions",
        lambda *_: [
            GeneratedQuestion(topic="Python", question="Что сделал проект?", target_agent="tech")
        ],
    )

    with TestClient(app) as client:
        response = client.post(
            "/v1/parse", files={"file": ("cv.pdf", b"%PDF fixture", "application/pdf")}
        )
    assert response.status_code == 200
    assert response.json()["parsed_resume"]["resume_topics"] == ["Python"]
    assert response.json()["questions"][0]["target_agent"] == "tech"


async def async_none():
    return None


def test_github_username_extraction_rejects_reserved_routes():
    assert extract_github_username("https://github.com/octocat/project") == "octocat"
    assert extract_github_username("https://github.com/orgs/example") is None
