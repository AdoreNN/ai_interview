from tests.test_sessions import VALID_SESSION, auth, register


def create_session(client, token: str) -> dict:
    response = client.post("/api/v1/sessions", json=VALID_SESSION, headers=auth(token))
    assert response.status_code == 201
    return response.json()


def test_interview_runs_to_completion_and_persists_state(client):
    user = register(client, "candidate@example.com")
    token = user["access_token"]
    session = create_session(client, token)

    started = client.post(
        f"/api/v1/sessions/{session['id']}/interview/start", headers=auth(token)
    )
    assert started.status_code == 200
    assert started.json()["status"] == "in_progress"
    assert started.json()["current_question"]
    assert started.json()["messages"][-1]["role"] == "assistant"

    resumed = client.get(
        f"/api/v1/sessions/{session['id']}/interview", headers=auth(token)
    )
    assert resumed.status_code == 200
    assert resumed.json()["messages"] == started.json()["messages"]

    turn = started
    for _ in range(10):
        turn = client.post(
            f"/api/v1/sessions/{session['id']}/interview/answer",
            headers=auth(token),
            json={"answer": "Я разобрал проблему, измерил результат и обсудил его с командой."},
        )
        assert turn.status_code == 200
        if turn.json()["status"] == "completed":
            break

    body = turn.json()
    assert body["status"] == "completed"
    assert body["current_question"] is None
    assert body["final_feedback"]["skill_averages"]
    assert len(body["evaluation_log"]) == 7

    retrieved = client.get(
        f"/api/v1/sessions/{session['id']}", headers=auth(token)
    ).json()
    assert retrieved["status"] == "completed"
    assert retrieved["interview_started"] is True


def test_interview_enforces_lifecycle_and_ownership(client):
    owner = register(client, "flow-owner@example.com")
    outsider = register(client, "flow-outsider@example.com")
    session = create_session(client, owner["access_token"])

    before_start = client.post(
        f"/api/v1/sessions/{session['id']}/interview/answer",
        headers=auth(owner["access_token"]),
        json={"answer": "Ответ"},
    )
    foreign = client.post(
        f"/api/v1/sessions/{session['id']}/interview/start",
        headers=auth(outsider["access_token"]),
    )
    first = client.post(
        f"/api/v1/sessions/{session['id']}/interview/start",
        headers=auth(owner["access_token"]),
    )
    duplicate = client.post(
        f"/api/v1/sessions/{session['id']}/interview/start",
        headers=auth(owner["access_token"]),
    )
    retrieve_before_start = client.get(
        f"/api/v1/sessions/{session['id']}/interview",
        headers=auth(outsider["access_token"]),
    )

    assert before_start.status_code == 409
    assert foreign.status_code == 404
    assert first.status_code == 200
    assert duplicate.status_code == 409
    assert retrieve_before_start.status_code == 404
