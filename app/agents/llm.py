from functools import lru_cache
from langchain_gigachat.chat_models import GigaChat
from app.core.config import get_settings

@lru_cache
def get_llm(temperature: float = 0.5) -> GigaChat:
    settings = get_settings()
    return GigaChat(
        credentials=settings.gigachat_credentials.get_secret_value(),
        verify_ssl_certs=False,
        model="GigaChat-2-Pro",
        temperature=temperature,
        max_tokens=1024,
    )