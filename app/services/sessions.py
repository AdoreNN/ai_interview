import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.interview_session import InterviewSession
from app.models.user import User
from app.schemas.interview_session import SessionCreate


def create_interview_session(
    db: Session, current_user: User, payload: SessionCreate
) -> InterviewSession:
    interview = InterviewSession(user_id=current_user.id, **payload.model_dump())
    db.add(interview)
    db.commit()
    db.refresh(interview)
    return interview


def list_interview_sessions(db: Session, current_user: User) -> list[InterviewSession]:
    statement = (
        select(InterviewSession)
        .where(InterviewSession.user_id == current_user.id)
        .order_by(InterviewSession.updated_at.desc(), InterviewSession.created_at.desc())
    )
    return list(db.scalars(statement).all())


def get_interview_session(
    db: Session, current_user: User, session_id: uuid.UUID
) -> InterviewSession:
    interview = db.scalar(
        select(InterviewSession).where(
            InterviewSession.id == session_id,
            InterviewSession.user_id == current_user.id,
        )
    )
    if interview is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return interview

