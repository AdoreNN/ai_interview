#!/bin/sh
set -eu

export UV_CACHE_DIR="${UV_CACHE_DIR:-/tmp/grillo-uv-cache}"
docker compose up -d --wait db
export DATABASE_URL="postgresql+psycopg://grillo:grillo@127.0.0.1:${POSTGRES_PORT:-5432}/grillo"
uv sync --locked
uv run --no-sync alembic stamp head
uv run --no-sync alembic downgrade base
uv run --no-sync alembic upgrade head
uv run --no-sync python scripts/check_schema.py present
uv run --no-sync alembic downgrade base
uv run --no-sync python scripts/check_schema.py absent
uv run --no-sync alembic upgrade head
echo "migration roundtrip verified"
