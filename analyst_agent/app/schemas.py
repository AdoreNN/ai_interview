from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

Level = Literal["intern", "junior", "middle", "senior"]
Band = Literal["weak", "basic", "good", "excellent"]



class DialogMessage(BaseModel):
    role: str = Field(description='"user" (кандидат) или "assistant" (интервьюер)')
    content: str


class EvaluationEntry(BaseModel):
    skill: str = Field(description='"<этап>.<тема>", например "tech.async" или "hr.teamwork"')
    score: int = Field(ge=0, le=10)
    reason: str = Field(default="", description="Обоснование оценки от интервьюера")


class InterviewData(BaseModel):
    model_config = ConfigDict(extra="ignore")

    session_id: str | None = None
    target_position: str | None = None
    experience_level: Level | None = None

    messages: list[DialogMessage] = Field(default_factory=list)
    evaluation_log: list[EvaluationEntry] = Field(default_factory=list)
    skills: dict[str, list[int]] = Field(default_factory=dict)
    weaknesses: list[str] = Field(default_factory=list)

    resume_topics: list[str] = Field(default_factory=list)
    resume_experience: dict[str, int] = Field(default_factory=dict)

    @model_validator(mode="before")
    @classmethod
    def _accept_state_typo(cls, values: Any) -> Any:
        # в InterviewState поле названо с опечаткой (resume_expirience) — принимаем оба написания
        if isinstance(values, dict) and "resume_expirience" in values and "resume_experience" not in values:
            values = {**values, "resume_experience": values["resume_expirience"]}
        return values


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str



class SkillStat(BaseModel):
    skill: str
    agent: str = Field(description="этап: hr / tech / manager")
    topic: str
    average: float
    count: int
    scores: list[int]


class Stats(BaseModel):
    answered_questions: int = Field(description="сколько ответов дал кандидат")
    overall_score: float | None = Field(
        default=None, description="средняя оценка по всем ответам, 0-10; null, если оценок нет"
    )
    overall_band: Band | None = Field(
        default=None,
        description="weak (<4), basic (4-6.9), good (7-8.9), excellent (>=9)",
    )
    overall_band_label: str | None = Field(
        default=None, description="то же по-русски: слабый / базовый / хороший / отличный"
    )
    is_preliminary: bool = Field(
        default=False, description="true, если оценок меньше трёх - выводы предварительные"
    )
    by_agent: dict[str, float] = Field(default_factory=dict, description="средняя оценка по этапам")
    skills: list[SkillStat] = Field(default_factory=list)
    strongest: list[str] = Field(default_factory=list, description="лучшие темы (skill)")
    weakest: list[str] = Field(default_factory=list, description="худшие темы (skill)")



class Feedback(BaseModel):
    summary: str = Field(description="Общее впечатление в 3-5 предложениях: уровень, главный вывод, что делать дальше.")
    strengths: list[str] = Field(description="Сильные стороны, подтверждённые оценками. Пустой список, если их нет.")
    weaknesses: list[str] = Field(description="Слабые места: конкретно что и по какой теме не получилось.")
    recommendations: list[str] = Field(description="Конкретные шаги: что изучить или потренировать, привязано к слабым темам.")


class FeedbackResponse(BaseModel):
    stats: Stats
    feedback: Feedback


class ChatRequest(BaseModel):
    interview: InterviewData
    feedback: Feedback | None = Field(default=None, description="Фидбек, выданный ранее; если не передан — отвечаем по данным интервью")
    history: list[ChatMessage] = Field(default_factory=list, description="Предыдущие реплики чата с аналитиком")
    question: str = Field(min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    answer: str
