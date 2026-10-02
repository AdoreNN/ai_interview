import httpx
from fastapi import HTTPException, status

from app.core.config import get_settings
from app.schemas.resume import ResumeParseResponse


async def parse_resume(filename: str, content_type: str, content: bytes) -> ResumeParseResponse:
    settings = get_settings()
    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.post(
                f"{settings.resume_parser_url.rstrip('/')}/v1/parse",
                files={"file": (filename, content, content_type)},
            )
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Resume parser is unavailable",
        ) from exc

    if response.status_code == 422:
        try:
            detail = response.json().get("detail", "Resume could not be parsed")
        except ValueError:
            detail = "Resume could not be parsed"
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)
    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Resume parser failed",
        )
    return ResumeParseResponse.model_validate(response.json())
