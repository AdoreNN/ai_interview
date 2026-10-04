import logging
from collections.abc import Callable
from functools import lru_cache
from typing import Any

from langchain_core.exceptions import OutputParserException
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_gigachat.chat_models import GigaChat
from pydantic import BaseModel, ValidationError

from app.config import get_settings

logger = logging.getLogger(__name__)

MAX_RETRIES = 2


class LLMOutputError(RuntimeError):
    """LLM не вернула валидный ответ после всех попыток"""


@lru_cache
def get_llm(temperature: float = 0.3) -> GigaChat:
    settings = get_settings()
    return GigaChat(
        credentials=settings.gigachat_credentials.get_secret_value(),
        scope=settings.gigachat_scope,
        model=settings.gigachat_model,
        verify_ssl_certs=settings.gigachat_verify_ssl,
        temperature=temperature,
        max_tokens=settings.max_tokens,
    )


def invoke_structured(
    schema: type[BaseModel],
    messages: list[BaseMessage],
    is_valid: Callable[[Any], bool] = lambda _: True,
    temperature: float = 0.3,
) -> Any:
    """Структурный вывод с ретраями. При отказе в следующую попытку добавляется подсказка,
    что не так, иначе модель просто повторяет ту же ошибку (три одинаковых попытки = одна)
    """
    llm = get_llm(temperature).with_structured_output(schema)
    msgs = list(messages)
    last_error: Exception | None = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            result = llm.invoke(msgs)
            if result is not None and is_valid(result):
                return result
            logger.warning("Rejected LLM output (attempt %s)", attempt + 1)
            msgs = [
                *messages,
                HumanMessage(
                    content=(
                        "Предыдущий ответ отклонён: не все поля заполнены осмысленно. "
                        "Заполни ВСЕ поля, summary и recommendations не должны быть пустыми."
                    )
                ),
            ]
        except (ValidationError, OutputParserException) as e:
            last_error = e
            logger.warning("Invalid LLM output (attempt %s): %s", attempt + 1, type(e).__name__)
    raise LLMOutputError(f"LLM не вернула валидный {schema.__name__}") from last_error


def invoke_text(messages: list[BaseMessage], temperature: float = 0.3) -> str:
    llm = get_llm(temperature)
    for attempt in range(MAX_RETRIES + 1):
        content = llm.invoke(messages).content
        text = content.strip() if isinstance(content, str) else ""
        if text:
            return text
        logger.warning("Empty LLM answer (attempt %s)", attempt + 1)
    raise LLMOutputError("LLM вернула пустой ответ")
