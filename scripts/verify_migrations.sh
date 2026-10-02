#!/bin/sh
set -eu

export UV_CACHE_DIR="${UV_CACHE_DIR:-/tmp/grillo-uv-cache}"
docker compose up -d --wait db
migration_db="grillo_migration_test"
db_user="${POSTGRES_USER:-grillo}"
cleanup() {
  docker compose exec -T db dropdb --if-exists --force -U "$db_user" "$migration_db" >/dev/null
}
trap cleanup EXIT
cleanup
docker compose exec -T db createdb -U "$db_user" "$migration_db"
export DATABASE_URL="postgresql+psycopg://${db_user}:${POSTGRES_PASSWORD:-grillo}@127.0.0.1:${POSTGRES_PORT:-5432}/${migration_db}"
uv sync --locked
uv run --no-sync alembic upgrade head
uv run --no-sync python scripts/check_schema.py present
uv run --no-sync alembic downgrade base
uv run --no-sync python scripts/check_schema.py absent
echo "migration roundtrip verified"
