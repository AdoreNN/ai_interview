from fastapi import FastAPI, HTTPException, UploadFile, status

from .config import get_settings
from .schemas import ParseResumeResponse
from .skills.generate_questions import generate_questions
from .skills.github_lookup import extract_github_username, fetch_github_profile
from .skills.read_resume import ResumeReadError, read_resume

app = FastAPI(title="pdf_parser_agent")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "agent": "pdf_parser_agent"}


@app.post("/v1/parse", response_model=ParseResumeResponse)
async def parse(file: UploadFile) -> ParseResumeResponse:
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=422, detail="Ожидается PDF-файл")
    limit = get_settings().max_resume_bytes
    pdf_bytes = await file.read(limit + 1)
    if len(pdf_bytes) > limit:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="PDF превышает допустимый размер",
        )

    try:
        parsed_resume, resume_text = read_resume(pdf_bytes)
    except ResumeReadError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e

    github_username = extract_github_username(resume_text)
    github_profile = await fetch_github_profile(github_username) if github_username else None

    questions = generate_questions(parsed_resume, resume_text, github_profile)

    return ParseResumeResponse(
        parsed_resume=parsed_resume, github_profile=github_profile, questions=questions
    )
