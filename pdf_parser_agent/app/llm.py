from functools import lru_cache
from typing import Any

from langchain_gigachat.chat_models import GigaChat

from .config import get_settings


class StubStructuredLLM:
    def __init__(self, schema: type):
        self.schema = schema

    def invoke(self, _: Any):
        if self.schema.__name__ == "ParsedResume":
            return self.schema(
                resume_topics=["Python"],
                resume_experience={},
                target_position="Python developer",
                experience_level="junior",
            )
        if self.schema.__name__ == "GeneratedQuestions":
            return self.schema(
                questions=[
                    {
                        "topic": "Python",
                        "question": "Как Python использовался в вашем последнем проекте?",
                        "target_agent": "tech",
                    }
                ]
            )
        raise ValueError(f"Unsupported stub schema: {self.schema.__name__}")


class StubLLM:
    def with_structured_output(self, schema: type) -> StubStructuredLLM:
        return StubStructuredLLM(schema)


@lru_cache
def get_llm(temperature: float = 0.3) -> GigaChat | StubLLM:
    settings = get_settings()
    if settings.llm_mode == "stub":
        return StubLLM()
    return GigaChat(
        credentials=settings.gigachat_credentials.get_secret_value(),
        scope=settings.gigachat_scope,
        model=settings.gigachat_model,
        verify_ssl_certs=settings.gigachat_verify_ssl,
        temperature=temperature,
        max_tokens=1024,
    )
