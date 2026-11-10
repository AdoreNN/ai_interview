from app.services.interviews import interview_progress

from tests.test_sessions import VALID_SESSION, auth, register


def state(**overrides) -> dict:
    data = {
        "pending_skill": "hr.motivation",
        "hr_count": 1, "max_hr": 3,
        "tech_count": 0, "max_tech": 4,
        "manager_count": 0, "max_manager": 3,
    }
    data.update(overrides)
    return data


def statuses(progress: dict) -> dict:
    return {s["agent"]: (s["status"], s["topics_done"], s["topics_total"]) for s in progress["stages"]}


def test_start_of_interview_has_hr_current_and_nothing_done():
    progress = interview_progress(state(), completed=False)
    assert statuses(progress) == {
        "hr": ("current", 0, 3),
        "tech": ("upcoming", 0, 4),
        "manager": ("upcoming", 0, 3),
    }
    assert progress["percent"] == 0


def test_middle_of_tech_stage_counts_finished_topics_only():
    progress = interview_progress(
        state(pending_skill="tech.sql", hr_count=3, tech_count=2), completed=False
    )
    assert statuses(progress) == {
        "hr": ("done", 3, 3),
        "tech": ("current", 1, 4),
        "manager": ("upcoming", 0, 3),
    }
    assert progress["percent"] == 40


def test_completed_interview_is_full():
    progress = interview_progress(state(pending_skill=None, hr_count=3, tech_count=4, manager_count=3), completed=True)
    assert all(s["status"] == "done" for s in progress["stages"])
    assert progress["percent"] == 100


def test_disabled_stage_is_hidden():
    progress = interview_progress(state(max_manager=0), completed=False)
    assert [s["agent"] for s in progress["stages"]] == ["hr", "tech"]


def test_interview_api_reports_progress(client):
    token = register(client, "progress@example.com")["access_token"]
    session = client.post("/api/v1/sessions", json=VALID_SESSION, headers=auth(token)).json()
    started = client.post(f"/api/v1/sessions/{session['id']}/interview/start", headers=auth(token)).json()
    assert started["progress"]["stages"][0] == {
        "agent": "hr", "topics_total": 3, "topics_done": 0, "status": "current",
    }

    turn = started
    for _ in range(30):
        turn = client.post(
            f"/api/v1/sessions/{session['id']}/interview/answer",
            headers=auth(token),
            json={"answer": "Измерил проблему и проверил результат."},
        ).json()
        if turn["status"] == "completed":
            break
    assert turn["progress"]["percent"] == 100
