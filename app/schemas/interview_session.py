from datetime import datetime
import uuid

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.interview_session import ExperienceLevel, SessionStatus


class SessionCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    target_position: str = Field(min_length=1, max_length=160)
    experience_level: ExperienceLevel

    @field_validator("title", "target_position")
    @classmethod
    def trim_non_empty_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("value must not be blank")
        return value


class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    target_position: str
    experience_level: ExperienceLevel
    status: SessionStatus
    created_at: datetime
    updated_at: datetime

