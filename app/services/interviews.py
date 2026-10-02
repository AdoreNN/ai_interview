from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.agents.graph import interview_graph
from app.core.config import get_settings
from app.models.interview_session import InterviewSession, SessionStatus


def _initial_state(interview: InterviewSession) -> dict:
    settings = get_settings()
    parsed = (interview.resume_context or {}).get("parsed_resume", {})
    return {
        "session_id": str(interview.id),
        "target_position": interview.target_position,
        "experience_level": interview.experience_level.value,
        "messages": [],
        "current_question": None,
        "last_user_answer": None,
        "resume_topics": parsed.get("resume_topics", []),
        "resume_experience": parsed.get("resume_experience", {}),
        "hr_count": 0,
        "tech_count": 0,
        "manager_count": 0,
        "max_hr": settings.interview_hr_questions,
        "max_tech": settings.interview_tech_questions,
        "max_manager": settings.interview_manager_questions,
        "skills": {},
        "pending_skill": None,
        "asked_topics": [],
        "weaknesses": [],
        "evaluation_log": [],
        "final_feedback": None,
        "finished": False,
    }


def _run_graph(state: dict) -> dict:
    try:
        return interview_graph.invoke(state)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Interview engine is unavailable",
        ) from exc


def _save_state(db: Session, interview: InterviewSession, state: dict) -> InterviewSession:
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
