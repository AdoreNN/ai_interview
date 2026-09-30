from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

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

    max_resume_chars: int = Field(default=12000, validation_alias="MAX_RESUME_CHARS")
    max_questions: int = Field(default=8, validation_alias="MAX_QUESTIONS")

    # опционально: поднимает лимит GitHub API с 60 до 5000 запросов/час
    github_token: SecretStr = Field(default=SecretStr(""), validation_alias="GITHUB_TOKEN")


@lru_cache
def get_settings() -> Settings:
    return Settings()
