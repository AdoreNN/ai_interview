from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

from app.models.interview_session import SessionStatus


class InterviewAnswer(BaseModel):
    answer: str = Field(min_length=1, max_length=10_000)

    @field_validator("answer")
    @classmethod
    def trim_answer(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("answer must not be blank")
        return value


class InterviewMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class InterviewResponse(BaseModel):
    status: SessionStatus
    current_question: str | None
    final_feedback: dict[str, Any] | None
    evaluation_log: list[dict[str, Any]]
    messages: list[InterviewMessage]
