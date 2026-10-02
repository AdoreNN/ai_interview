from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_env: Literal["development", "test", "production"] = Field(
        default="development", validation_alias="APP_ENV"
    )
    database_url: str = Field(validation_alias="DATABASE_URL")
    jwt_secret: SecretStr = Field(validation_alias="JWT_SECRET", min_length=32)
    jwt_algorithm: str = Field(default="HS256", validation_alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=30, ge=1, le=1440, validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    allowed_origins: str = Field(
        default="http://localhost:3000", validation_alias="ALLOWED_ORIGINS"
    )
    # gigachat
    gigachat_credentials: SecretStr = Field(
        default=SecretStr(""), validation_alias="GIGACHAT_CREDENTIALS"
    )
    gigachat_scope: str = Field(
        default="GIGACHAT_API_PERS", validation_alias="GIGACHAT_SCOPE"
    )
    gigachat_model: str = Field(
        default="GigaChat-2-Pro", validation_alias="GIGACHAT_MODEL"
    )
    gigachat_verify_ssl: bool = Field(
        default=False, validation_alias="GIGACHAT_VERIFY_SSL"
    )
    llm_mode: Literal["gigachat", "stub"] = Field(
        default="gigachat", validation_alias="LLM_MODE"
    )
    resume_parser_url: str = Field(
        default="http://resume-parser:8000", validation_alias="RESUME_PARSER_URL"
    )
    max_resume_bytes: int = Field(
        default=5_000_000, ge=1, le=20_000_000, validation_alias="MAX_RESUME_BYTES"
    )
    interview_hr_questions: int = Field(
        default=2, ge=0, le=10, validation_alias="INTERVIEW_HR_QUESTIONS"
    )
    interview_tech_questions: int = Field(
        default=3, ge=0, le=20, validation_alias="INTERVIEW_TECH_QUESTIONS"
    )
    interview_manager_questions: int = Field(
        default=2, ge=0, le=10, validation_alias="INTERVIEW_MANAGER_QUESTIONS"
    )

    @field_validator("database_url")
    @classmethod
    def database_url_must_use_postgresql(cls, value: str) -> str:
        if not value.startswith(("postgresql://", "postgresql+psycopg://")):
            raise ValueError("DATABASE_URL must be a PostgreSQL URL")
        return value

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
