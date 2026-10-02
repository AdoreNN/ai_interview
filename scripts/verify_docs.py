from pathlib import Path


def require(contents: str, values: list[str], source: str) -> None:
    missing = [value for value in values if value not in contents]
    if missing:
        raise SystemExit(f"{source} is missing: {', '.join(missing)}")


def main() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")
    require(
        readme,
        [
            "docker compose up --build",
            "alembic upgrade head",
            "pytest",
            "GET /health",
            "POST /api/v1/auth/sign-up",
            "POST /api/v1/auth/sign-in",
            "POST /api/v1/sessions",
            "GET /api/v1/sessions",
            "GET /api/v1/sessions/{session_id}",
            "POST /api/v1/sessions/{session_id}/resume",
            "POST /api/v1/sessions/{session_id}/interview/start",
            "POST /api/v1/sessions/{session_id}/interview/answer",
            "LLM_MODE",
            "scripts/verify_stack.sh",
        ],
        "README.md",
    )
    require(
        Path(".env.example").read_text(encoding="utf-8"),
        ["DATABASE_URL", "JWT_SECRET", "LLM_MODE", "RESUME_PARSER_URL", "MAX_RESUME_BYTES"],
        ".env.example",
    )
    require(
        Path("docker-compose.yml").read_text(encoding="utf-8"),
        ["backend:", "resume-parser:", "db:", "healthcheck:", "LLM_MODE"],
        "docker-compose.yml",
    )
    print("documentation contract verified")


if __name__ == "__main__":
    main()
