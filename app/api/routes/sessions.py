import uuid

from fastapi import APIRouter, status

from app.api.dependencies import CurrentUser, DbSession
from app.schemas.interview_session import SessionCreate, SessionResponse
from app.services.sessions import (
    create_interview_session,
    get_interview_session,
    list_interview_sessions,
)


router = APIRouter(prefix="/sessions", tags=["interview-sessions"])


@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(
    payload: SessionCreate, db: DbSession, current_user: CurrentUser
) -> SessionResponse:
    return SessionResponse.model_validate(create_interview_session(db, current_user, payload))


@router.get("", response_model=list[SessionResponse])
def list_sessions(db: DbSession, current_user: CurrentUser) -> list[SessionResponse]:
    return [
        SessionResponse.model_validate(item)
        for item in list_interview_sessions(db, current_user)
    ]


@router.get("/{session_id}", response_model=SessionResponse)
def retrieve_session(
    session_id: uuid.UUID, db: DbSession, current_user: CurrentUser
) -> SessionResponse:
    return SessionResponse.model_validate(get_interview_session(db, current_user, session_id))

