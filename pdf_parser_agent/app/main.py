from fastapi import FastAPI, HTTPException, UploadFile

from app.schemas import ParseResumeResponse
from app.skills.generate_questions import generate_questions
from app.skills.github_lookup import extract_github_username, fetch_github_profile
from app.skills.read_resume import ResumeReadError, read_resume

app = FastAPI(title="pdf_parser_agent")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "agent": "pdf_parser_agent"}


@app.post("/v1/parse", response_model=ParseResumeResponse)
async def parse(file: UploadFile) -> ParseResumeResponse:
    pdf_bytes = await file.read()

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
