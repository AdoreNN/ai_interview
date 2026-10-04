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

    gigachat_credentials: SecretStr = Field(default=SecretStr(""), validation_alias="GIGACHAT_CREDENTIALS")
    gigachat_scope: str = Field(default="GIGACHAT_API_PERS", validation_alias="GIGACHAT_SCOPE")
    gigachat_model: str = Field(default="GigaChat-2-Pro", validation_alias="GIGACHAT_MODEL")
    gigachat_verify_ssl: bool = Field(default=False, validation_alias="GIGACHAT_VERIFY_SSL")

    max_tokens: int = Field(default=2048, validation_alias="MAX_TOKENS")
    max_dialog_chars: int = Field(default=12000, validation_alias="MAX_DIALOG_CHARS")
    max_message_chars: int = Field(default=1500, validation_alias="MAX_MESSAGE_CHARS")
    max_chat_history: int = Field(default=20, validation_alias="MAX_CHAT_HISTORY")


@lru_cache
def get_settings() -> Settings:
    return Settings()
