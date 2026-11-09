import logging

import httpx
from fastapi import HTTPException, status

from app.core.config import get_settings

logger = logging.getLogger(__name__)


def build_feedback(state: dict) -> dict | None:
    """Итоговый разбор интервью от analyst_agent; None, если сервис недоступен."""
    settings = get_settings()
    try:
        response = httpx.post(
            f"{settings.analyst_url.rstrip('/')}/v1/feedback",
            json=state,
            timeout=settings.analyst_timeout,
        )
        response.raise_for_status()
        return response.json()
    except (httpx.HTTPError, ValueError) as exc:
        logger.warning("Analyst feedback unavailable: %s", type(exc).__name__)
        return None


def answer_question(interview: dict, feedback: dict | None, history: list[dict], question: str) -> str:
    settings = get_settings()
    try:
        response = httpx.post(
            f"{settings.analyst_url.rstrip('/')}/v1/chat",
            json={
                "interview": interview,
                "feedback": feedback,
                "history": history,
                "question": question,
            },
            timeout=settings.analyst_timeout,
        )
        response.raise_for_status()
        return response.json()["answer"]
    except (httpx.HTTPError, ValueError, KeyError) as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Analyst is unavailable",
        ) from exc
