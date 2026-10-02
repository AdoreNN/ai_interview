"""Add resume context and persisted interview state.

Revision ID: 20261002_0002
Revises: 20260926_0001
Create Date: 2026-10-02
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20261002_0002"
down_revision: str | None = "20260926_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    columns = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("sessions")}
    if "resume_context" not in columns:
        op.add_column("sessions", sa.Column("resume_context", sa.JSON(), nullable=True))
    if "interview_state" not in columns:
        op.add_column("sessions", sa.Column("interview_state", sa.JSON(), nullable=True))


def downgrade() -> None:
    columns = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("sessions")}
    if "interview_state" in columns:
        op.drop_column("sessions", "interview_state")
    if "resume_context" in columns:
        op.drop_column("sessions", "resume_context")
