import os
import sys

from sqlalchemy import create_engine, inspect


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in {"present", "absent"}:
        raise SystemExit("usage: check_schema.py present|absent")

    engine = create_engine(os.environ["DATABASE_URL"])
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    domain_tables = {"users", "sessions"}

    if sys.argv[1] == "present":
        if not domain_tables.issubset(tables):
            raise SystemExit(f"missing domain tables: {sorted(domain_tables - tables)}")
        if set(inspector.get_foreign_keys("sessions")[0]["referred_columns"]) != {"id"}:
            raise SystemExit("sessions.user_id foreign key is invalid")
        indexes = {item["name"] for item in inspector.get_indexes("sessions")}
        if "ix_sessions_user_id" not in indexes:
            raise SystemExit("sessions.user_id index is missing")
        columns = {item["name"] for item in inspector.get_columns("sessions")}
        required_columns = {"resume_context", "interview_state"}
        if not required_columns.issubset(columns):
            raise SystemExit(
                f"missing integrated session columns: {sorted(required_columns - columns)}"
            )
    elif domain_tables & tables:
        raise SystemExit(f"domain tables still present: {sorted(domain_tables & tables)}")


if __name__ == "__main__":
    main()
