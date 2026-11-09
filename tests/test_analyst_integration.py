from types import SimpleNamespace

from app.agents.nodes.base import _build_prompt
from app.agents.prompts.hr import HR_SYSTEM_PROMPT
from app.agents.prompts.tech import TECH_SYSTEM_PROMPT
from app.services.interviews import _initial_state

from tests.test_sessions import VALID_SESSION, auth, register


REPORT = {
    "stats": {"overall_score": 7.0, "overall_band_label": "хороший"},
    "feedback": {
        "summary": "Уверенный результат.",
        "strengths": ["SQL"],
        "weaknesses": ["Планирование"],
        "recommendations": ["Разобрать декомпозицию задач"],
    },
}


def run_interview(client, token: str) -> dict:
    session = client.post("/api/v1/sessions", json=VALID_SESSION, headers=auth(token)).json()
    client.post(f"/api/v1/sessions/{session['id']}/interview/start", headers=auth(token))
    for _ in range(10):
        turn = client.post(
            f"/api/v1/sessions/{session['id']}/interview/answer",
            headers=auth(token),
            json={"answer": "Измерил проблему, изменил план и проверил результат."},
        ).json()
        if turn["status"] == "completed":
            return {"session": session, "turn": turn}
    raise AssertionError("interview did not complete")


def test_completed_interview_gets_analyst_report(client, monkeypatch):
    calls = []
    monkeypatch.setattr(
        "app.services.analyst.build_feedback", lambda state: calls.append(state) or REPORT
    )
    user = register(client, "analyst-ok@example.com")
    result = run_interview(client, user["access_token"])

    feedback = result["turn"]["final_feedback"]
    assert feedback["analyst"] == REPORT
    assert feedback["skill_averages"]
    assert len(calls) == 1
    assert calls[0]["finished"] is True


def test_interview_completes_without_analyst(client, monkeypatch):
    monkeypatch.setattr("app.services.analyst.build_feedback", lambda state: None)
    user = register(client, "analyst-down@example.com")
    result = run_interview(client, user["access_token"])

    assert result["turn"]["status"] == "completed"
    assert "analyst" not in result["turn"]["final_feedback"]


def test_analyst_chat_requires_completed_interview_and_owner(client, monkeypatch):
    seen = {}

    def fake_answer(interview, feedback, history, question):
        seen.update(feedback=feedback, history=history, question=question)
        return "Начните с планирования."

    monkeypatch.setattr("app.services.analyst.build_feedback", lambda state: REPORT)
    monkeypatch.setattr("app.services.analyst.answer_question", fake_answer)

    owner = register(client, "chat-owner@example.com")
    outsider = register(client, "chat-outsider@example.com")
    session = client.post(
        "/api/v1/sessions", json=VALID_SESSION, headers=auth(owner["access_token"])
    ).json()
    url = f"/api/v1/sessions/{session['id']}/feedback/chat"
    payload = {"question": "С чего начать?", "history": []}

    not_started = client.post(url, json=payload, headers=auth(owner["access_token"]))
    assert not_started.status_code == 409

    completed = run_interview(client, owner["access_token"])
    url = f"/api/v1/sessions/{completed['session']['id']}/feedback/chat"
    answer = client.post(url, json=payload, headers=auth(owner["access_token"]))
    foreign = client.post(url, json=payload, headers=auth(outsider["access_token"]))
    blank = client.post(
        url, json={"question": "   ", "history": []}, headers=auth(owner["access_token"])
    )

    assert answer.status_code == 200
    assert answer.json() == {"answer": "Начните с планирования."}
    assert seen["feedback"] == REPORT["feedback"]
    assert seen["question"] == "С чего начать?"
    assert foreign.status_code == 404
    assert blank.status_code == 422


def test_resume_questions_are_grouped_by_agent_and_reach_prompts():
    interview = SimpleNamespace(
        id="s1",
        target_position="Python developer",
        experience_level=SimpleNamespace(value="middle"),
        resume_context={
            "parsed_resume": {"resume_topics": ["Python"], "resume_experience": {}},
            "questions": [
                {"topic": "Kafka", "question": "Расскажите про Kafka в проекте X", "target_agent": "tech"},
                {"topic": "gap", "question": "Почему был перерыв в 2024?", "target_agent": "hr"},
            ],
        },
    )
    state = _initial_state(interview)
    assert state["resume_questions"] == {
        "tech": ["Расскажите про Kafka в проекте X"],
        "hr": ["Почему был перерыв в 2024?"],
    }

    tech_prompt = _build_prompt(state, TECH_SYSTEM_PROMPT, "tech_count", "max_tech", "tech")
    hr_prompt = _build_prompt(state, HR_SYSTEM_PROMPT, "hr_count", "max_hr", "hr")
    manager_free = _build_prompt(state, HR_SYSTEM_PROMPT, "hr_count", "max_hr", "manager")

    assert "Kafka в проекте X" in tech_prompt and "перерыв" not in tech_prompt
    assert "перерыв в 2024" in hr_prompt and "Kafka" not in hr_prompt
    assert "ВОПРОСЫ ПО РЕЗЮМЕ" not in manager_free


def test_prompt_is_unchanged_without_resume_questions():
    state = {"hr_count": 0, "max_hr": 2}
    assert "ВОПРОСЫ ПО РЕЗЮМЕ" not in _build_prompt(state, HR_SYSTEM_PROMPT, "hr_count", "max_hr", "hr")
