#!/bin/sh
set -eu

export UV_CACHE_DIR="${UV_CACHE_DIR:-/tmp/grillo-uv-cache}"
docker compose up -d --build --wait
uv run --no-sync python scripts/smoke_api.py
echo "containerized backend verified"
