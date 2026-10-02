#!/bin/sh
set -eu

export UV_CACHE_DIR="${UV_CACHE_DIR:-/tmp/grillo-uv-cache}"
docker compose up -d --wait db
test_db="grillo_test"
db_user="${POSTGRES_USER:-grillo}"
cleanup() {
  docker compose exec -T db dropdb --if-exists --force -U "$db_user" "$test_db" >/dev/null
}
trap cleanup EXIT
cleanup
docker compose exec -T db createdb -U "$db_user" "$test_db"
export APP_ENV=test
export DATABASE_URL="postgresql+psycopg://${db_user}:${POSTGRES_PASSWORD:-grillo}@127.0.0.1:${POSTGRES_PORT:-5432}/${test_db}"
export JWT_SECRET="test-secret-with-at-least-thirty-two-characters"
export LLM_MODE=stub
uv sync --locked
uv run --no-sync pytest -q
echo "integrated test suite passed"
