import uuid

from fastapi import APIRouter, HTTPException, status

from app.api.dependencies import CurrentUser, DbSession
from app.schemas.interview import (
    AnalystChatRequest,
    AnalystChatResponse,
    InterviewAnswer,
    InterviewResponse,
)
from app.models.interview_session import SessionStatus
from app.services.interviews import (
    answer_interview,
    ask_analyst,
    interview_progress,
    start_interview,
)
from app.services.sessions import get_interview_session


router = APIRouter(prefix="/sessions", tags=["interview-dialogue"])


def _response(interview) -> InterviewResponse:
    state = interview.interview_state or {}
    return InterviewResponse(
        status=interview.status,
        current_question=state.get("current_question"),
        final_feedback=state.get("final_feedback"),
        evaluation_log=state.get("evaluation_log", []),
        messages=state.get("messages", []),
        progress=interview_progress(state, interview.status == SessionStatus.COMPLETED),
    )


@router.get("/{session_id}/interview", response_model=InterviewResponse)
def retrieve(
    session_id: uuid.UUID, db: DbSession, current_user: CurrentUser
) -> InterviewResponse:
    interview = get_interview_session(db, current_user, session_id)
    if interview.interview_state is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Interview not started",
        )
    return _response(interview)


@router.post("/{session_id}/interview/start", response_model=InterviewResponse)
def start(
    session_id: uuid.UUID, db: DbSession, current_user: CurrentUser
) -> InterviewResponse:
    interview = get_interview_session(db, current_user, session_id)
    return _response(start_interview(db, interview))


@router.post("/{session_id}/interview/answer", response_model=InterviewResponse)
def answer(
    session_id: uuid.UUID,
    payload: InterviewAnswer,
    db: DbSession,
    current_user: CurrentUser,
) -> InterviewResponse:
    interview = get_interview_session(db, current_user, session_id)
    return _response(answer_interview(db, interview, payload.answer))


@router.post("/{session_id}/feedback/chat", response_model=AnalystChatResponse)
def chat_with_analyst(
    session_id: uuid.UUID,
    payload: AnalystChatRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> AnalystChatResponse:
    interview = get_interview_session(db, current_user, session_id)
    history = [m.model_dump() for m in payload.history]
    return AnalystChatResponse(answer=ask_analyst(interview, payload.question, history))
