import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_required_settings_are_rejected_when_missing(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("JWT_SECRET", raising=False)
    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_non_postgresql_database_url_is_rejected():
    with pytest.raises(ValidationError):
        Settings(
            DATABASE_URL="sqlite:///local.db",
            JWT_SECRET="a-secret-that-is-long-enough-for-tests",
            _env_file=None,
        )


def test_allowed_origins_are_parsed():
    settings = Settings(
        DATABASE_URL="postgresql+psycopg://user:pass@localhost/db",
        JWT_SECRET="a-secret-that-is-long-enough-for-tests",
        ALLOWED_ORIGINS="http://localhost:3000, https://example.com ",
        _env_file=None,
    )
    assert settings.cors_origins == ["http://localhost:3000", "https://example.com"]

