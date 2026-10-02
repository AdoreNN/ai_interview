from typing import Literal

from pydantic import BaseModel, Field


class ParsedResume(BaseModel):
    """Результат skill 1 (чтение и разбор PDF)."""

    resume_topics: list[str] = Field(description="Технологии и навыки, упомянутые в резюме")
    resume_experience: dict[str, int] = Field(
        description="Опыт в годах по темам из resume_topics, если его можно оценить"
    )
    target_position: str | None = Field(
        default=None, description="Позиция, на которую похоже претендует кандидат"
    )
    experience_level: Literal["intern", "junior", "middle", "senior"] | None = Field(
        default=None, description="Оценка уровня кандидата по резюме"
    )


class GeneratedQuestion(BaseModel):
    """Один вопрос из skill 2 (генерация вопросов), для последующей раздачи агентам-собеседователям оркестратором."""

    topic: str = Field(description="Тема вопроса, например конкретная технология из резюме")
    question: str = Field(description="Текст вопроса кандидату")
    target_agent: Literal["tech", "hr", "manager"] = Field(
        description="Какому агенту-собеседователю передать этот вопрос"
    )


class GeneratedQuestions(BaseModel):
    """Обёртка над списком вопросов — нужна для structured output GigaChat."""

    questions: list[GeneratedQuestion] = Field(description="Сгенерированные вопросы по резюме")


class GithubRepo(BaseModel):
    """Один репозиторий кандидата (не форк), из skill 3 (github_lookup)."""

    name: str
    description: str | None = None
    language: str | None = None
    stars: int = 0
    url: str


class GithubProfile(BaseModel):
    """Результат skill 3: публичный профиль GitHub, если ссылка нашлась в резюме."""

    username: str
    name: str | None = None
    bio: str | None = None
    public_repos: int = 0
    profile_url: str
    top_repos: list[GithubRepo] = Field(default_factory=list)


class ParseResumeResponse(BaseModel):
    parsed_resume: ParsedResume
    github_profile: GithubProfile | None = None
    questions: list[GeneratedQuestion]
