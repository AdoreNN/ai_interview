import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import app

SAMPLE = json.loads(
    (Path(__file__).resolve().parent.parent / "samples" / "sample_state.json").read_text()
)


@pytest.fixture
def stub_client(monkeypatch):
    monkeypatch.setenv("LLM_MODE", "stub")
    get_settings.cache_clear()
    yield TestClient(app)
    get_settings.cache_clear()


def test_feedback_works_without_llm(stub_client):
    response = stub_client.post("/v1/feedback", json=SAMPLE)

    assert response.status_code == 200
    body = response.json()
    assert body["stats"]["overall_score"] == 5.8  # статистику считает код, не LLM
    assert body["feedback"]["summary"]
    assert body["feedback"]["recommendations"]


def test_chat_works_without_llm(stub_client):
    response = stub_client.post(
        "/v1/chat", json={"interview": SAMPLE, "question": "С чего начать?"}
    )

    assert response.status_code == 200
    assert response.json()["answer"]
