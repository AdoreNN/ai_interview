FROM ghcr.io/astral-sh/uv:0.11.15 AS uv

FROM python:3.12-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app
COPY --from=uv /uv /uvx /bin/
COPY pyproject.toml uv.lock README.md ./
COPY app ./app
RUN uv sync --frozen --no-dev --no-editable

FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:${PATH}"

RUN addgroup --system grillo && adduser --system --ingroup grillo --home /home/grillo grillo

WORKDIR /app
COPY --from=builder --chown=grillo:grillo /app/.venv /app/.venv

COPY alembic.ini ./
COPY alembic ./alembic
COPY scripts/start.sh ./scripts/start.sh

USER grillo
EXPOSE 8000

CMD ["sh", "scripts/start.sh"]
