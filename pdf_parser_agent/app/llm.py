from functools import lru_cache

from langchain_gigachat.chat_models import GigaChat

from app.config import get_settings


@lru_cache
def get_llm(temperature: float = 0.3) -> GigaChat:
    settings = get_settings()
    return GigaChat(
        credentials=settings.gigachat_credentials.get_secret_value(),
        scope=settings.gigachat_scope,
        model=settings.gigachat_model,
        verify_ssl_certs=settings.gigachat_verify_ssl,
        temperature=temperature,
        max_tokens=1024,
    )
