import uuid

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.api.dependencies import CurrentUser, DbSession
from app.core.config import get_settings
from app.schemas.resume import ResumeParseResponse
from app.services.resume_parser import parse_resume
from app.services.sessions import get_interview_session


router = APIRouter(prefix="/sessions", tags=["resume-analysis"])


@router.post("/{session_id}/resume", response_model=ResumeParseResponse)
async def upload_resume(
    session_id: uuid.UUID,
    db: DbSession,
    current_user: CurrentUser,
    file: UploadFile = File(...),
) -> ResumeParseResponse:
    interview = get_interview_session(db, current_user, session_id)
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Only application/pdf files are accepted",
        )
    limit = get_settings().max_resume_bytes
    content = await file.read(limit + 1)
    if len(content) > limit:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Resume file is too large",
        )
    result = await parse_resume(file.filename or "resume.pdf", file.content_type, content)
    interview.resume_context = result.model_dump(mode="json")
    db.add(interview)
    db.commit()
    return result
