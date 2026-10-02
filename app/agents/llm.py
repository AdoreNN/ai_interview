from functools import lru_cache
from typing import Any

from langchain_gigachat.chat_models import GigaChat

from app.core.config import get_settings


class StubStructuredLLM:
    def __init__(self, schema: type):
        self.schema = schema

    def invoke(self, _: Any):
        payloads = {
            "HRTurn": {
                "reason": "Локальная stub-оценка.",
                "evaluation": 7,
                "weakness": None,
                "question": "Расскажите о сложной командной ситуации и вашей личной роли.",
                "topic": "teamwork",
            },
            "TechTurn": {
                "reason": "Локальная stub-оценка.",
                "evaluation": 7,
                "weakness": None,
                "question": "Как вы диагностируете медленный SQL-запрос в production?",
                "topic": "sql",
                "difficulty": "middle",
            },
            "ManagerTurn": {
                "reason": "Локальная stub-оценка.",
                "evaluation": 7,
                "weakness": None,
                "question": "Как вы оценивали сроки задачи при неполных требованиях?",
                "topic": "planning",
            },
            "StageEval": {
                "reason": "Локальная stub-оценка для запуска без внешнего LLM.",
                "evaluation": 7,
                "weakness": None,
            },
        }
        return self.schema(**payloads[self.schema.__name__])


class StubLLM:
    def with_structured_output(self, schema: type) -> StubStructuredLLM:
        return StubStructuredLLM(schema)


@lru_cache
def get_llm(temperature: float = 0.5) -> GigaChat | StubLLM:
    settings = get_settings()
    if settings.llm_mode == "stub":
        return StubLLM()
    return GigaChat(
        credentials=settings.gigachat_credentials.get_secret_value(),
        scope=settings.gigachat_scope,
        verify_ssl_certs=settings.gigachat_verify_ssl,
        model=settings.gigachat_model,
        temperature=temperature,
        max_tokens=1024,
    )
