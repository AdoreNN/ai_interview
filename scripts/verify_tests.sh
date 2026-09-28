#!/bin/sh
set -eu

export UV_CACHE_DIR="${UV_CACHE_DIR:-/tmp/grillo-uv-cache}"
docker compose up -d --wait db
export APP_ENV=test
export DATABASE_URL="postgresql+psycopg://grillo:grillo@127.0.0.1:${POSTGRES_PORT:-5432}/grillo"
export JWT_SECRET="test-secret-with-at-least-thirty-two-characters"
uv sync --locked
uv run --no-sync pytest -q
echo "backend test suite passed"
