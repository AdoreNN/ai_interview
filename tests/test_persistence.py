import uuid

import pytest
from sqlalchemy import inspect, text
from sqlalchemy.exc import IntegrityError

from app.db.session import SessionLocal, engine
from app.models.interview_session import ExperienceLevel, InterviewSession


def test_database_connection_and_domain_tables():
    with engine.connect() as connection:
        assert connection.scalar(text("SELECT 1")) == 1
    tables = set(inspect(engine).get_table_names())
    assert {"users", "sessions"}.issubset(tables)


def test_orphan_session_is_rejected():
    with SessionLocal() as db:
        db.add(
            InterviewSession(
                user_id=uuid.uuid4(),
                title="Orphan",
                target_position="Backend developer",
                experience_level=ExperienceLevel.JUNIOR,
            )
        )
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()
