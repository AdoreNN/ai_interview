from __future__ import annotations

import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Enum as SqlEnum
from sqlalchemy import ForeignKey, Index, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class ExperienceLevel(str, enum.Enum):
    INTERN = "intern"
    JUNIOR = "junior"
    MIDDLE = "middle"
    SENIOR = "senior"


class SessionStatus(str, enum.Enum):
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


def enum_values(enum_type: type[enum.Enum]) -> list[str]:
    return [item.value for item in enum_type]


class InterviewSession(TimestampMixin, Base):
    __tablename__ = "sessions"
    __table_args__ = (Index("ix_sessions_user_id", "user_id"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    target_position: Mapped[str] = mapped_column(String(160), nullable=False)
    experience_level: Mapped[ExperienceLevel] = mapped_column(
        SqlEnum(
            ExperienceLevel,
            name="experience_level",
            native_enum=False,
            create_constraint=True,
            values_callable=enum_values,
        ),
        nullable=False,
    )
    status: Mapped[SessionStatus] = mapped_column(
        SqlEnum(
            SessionStatus,
            name="session_status",
            native_enum=False,
            create_constraint=True,
            values_callable=enum_values,
        ),
        nullable=False,
        default=SessionStatus.CREATED,
        server_default=SessionStatus.CREATED.value,
    )
    resume_context: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    interview_state: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    user: Mapped["User"] = relationship(back_populates="sessions")
