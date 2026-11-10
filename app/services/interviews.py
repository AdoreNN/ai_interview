import logging

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.agents.graph import interview_graph
from app.agents.routing import STAGES
from app.services import analyst
from app.core.config import get_settings
from app.models.interview_session import InterviewSession, SessionStatus

logger = logging.getLogger(__name__)


def _initial_state(interview: InterviewSession) -> dict:
    settings = get_settings()
    resume_context = interview.resume_context or {}
    parsed = resume_context.get("parsed_resume", {})
    resume_questions: dict[str, list[str]] = {}
    for item in resume_context.get("questions", []):
        resume_questions.setdefault(item["target_agent"], []).append(item["question"])
    return {
        "session_id": str(interview.id),
        "target_position": interview.target_position,
        "experience_level": interview.experience_level.value,
        "messages": [],
        "current_question": None,
        "last_user_answer": None,
        "resume_topics": parsed.get("resume_topics", []),
        "resume_experience": parsed.get("resume_experience", {}),
        "resume_questions": resume_questions,
        "hr_count": 0,
        "tech_count": 0,
        "manager_count": 0,
        "max_hr": settings.interview_hr_topics,
        "max_tech": settings.interview_tech_topics,
        "max_manager": settings.interview_manager_topics,
        "followups": 0,
        "max_followups": settings.interview_max_followups,
        "skills": {},
        "pending_skill": None,
        "asked_topics": [],
        "weaknesses": [],
        "evaluation_log": [],
        "final_feedback": None,
        "finished": False,
    }


def interview_progress(state: dict, completed: bool) -> dict:
    """Этапы и доля пройденных тем; текущая тема считается начатой, но не пройденной."""
    order = [agent for agent, _, _ in STAGES]
    current = (state.get("pending_skill") or "").split(".")[0]
    current_index = order.index(current) if current in order else None
    stages = []
    for index, (agent, count_key, max_key) in enumerate(STAGES):
        total = state.get(max_key, 0)
        if total <= 0:
            continue
        count = min(state.get(count_key, 0), total)
        if completed or (current_index is not None and index < current_index):
            stage_status, done = "done", total
        elif index == current_index:
            stage_status, done = "current", max(count - 1, 0)
        elif current_index is None and count >= total:
            stage_status, done = "done", total
        else:
            stage_status, done = "upcoming", 0
        stages.append(
            {"agent": agent, "topics_total": total, "topics_done": done, "status": stage_status}
        )
    all_topics = sum(stage["topics_total"] for stage in stages)
    done_topics = sum(stage["topics_done"] for stage in stages)
    percent = 100 if completed else (round(100 * done_topics / all_topics) if all_topics else 0)
    return {"percent": percent, "stages": stages}


def _run_graph(state: dict) -> dict:
    try:
        return interview_graph.invoke(state)
    except Exception as exc:
        logger.exception("Interview graph failed")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Interview engine is unavailable",
        ) from exc


def _attach_analyst_feedback(state: dict) -> dict:
    """Дополняет базовый final_feedback разбором analyst_agent, если он доступен."""
    feedback = state.get("final_feedback")
    if not state.get("finished") or feedback is None or "analyst" in feedback:
        return state
    report = analyst.build_feedback(state)
    if report is None:
        return state
    return {**state, "final_feedback": {**feedback, "analyst": report}}


def _save_state(db: Session, interview: InterviewSession, state: dict) -> InterviewSession:
    state = _attach_analyst_feedback(state)
    interview.interview_state = state
    interview.status = (
        SessionStatus.COMPLETED if state.get("finished") else SessionStatus.IN_PROGRESS
    )
    db.add(interview)
    db.commit()
    db.refresh(interview)
    return interview


def start_interview(db: Session, interview: InterviewSession) -> InterviewSession:
    if interview.interview_state is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Interview already started")
    return _save_state(db, interview, _run_graph(_initial_state(interview)))


def answer_interview(
    db: Session, interview: InterviewSession, answer: str
) -> InterviewSession:
    if interview.interview_state is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Interview not started")
    if interview.status == SessionStatus.COMPLETED:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Interview completed")

    state = dict(interview.interview_state)
    state["messages"] = [
        *state.get("messages", []),
        {"role": "user", "content": answer},
    ]
    state["last_user_answer"] = answer
    return _save_state(db, interview, _run_graph(state))


def ask_analyst(interview: InterviewSession, question: str, history: list[dict]) -> str:
    if interview.status != SessionStatus.COMPLETED or interview.interview_state is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Interview is not completed yet",
        )
    state = interview.interview_state
    report = (state.get("final_feedback") or {}).get("analyst") or {}
    return analyst.answer_question(state, report.get("feedback"), history, question)
