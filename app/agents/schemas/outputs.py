from typing import Literal
from pydantic import BaseModel, Field

Level = Literal["intern", "junior", "middle", "senior"]

class _TurnBase(BaseModel):
    """Ход интервьюера: оценка предыдущего ответа и следующий вопрос."""
    # порядок полей важен, не меняйте пж
    # обоснование - балл - диагноз - вопрос
    reason: str = Field(
        default="",
        description="Обоснование оценки предыдущего ответа. Пусто, если ответа ещё не было.",
    )
    evaluation: int | None = Field(
        default=None, ge=0, le=10,
        description="Оценка последнего ответа кандидата 0-10. Обязательна, если кандидат уже отвечал. null только в самом первом ходе.",
    )
    weakness: str | None = Field(
        default=None,
        description="Конкретная слабость кандидата, выявленная в ответе, или null.",
    )
    question: str = Field(
        description="Следующий вопрос кандидату."
    )

class HRTurn(_TurnBase):
    """Ход HR-интервьюера: оценка предыдущего ответа кандидата и следующий вопрос по soft skills."""
    agent_type: Literal["hr"]="hr"
    topic: Literal["motivation", "teamwork", "stress", "conflict", "growth"]

class TechTurn(_TurnBase):
    """Ход технического интервьюера: оценка предыдущего ответа кандидата и следующий технический вопрос."""
    agent_type: Literal["tech"]="tech"
    topic: Literal["python_basics", "decorators", "async", "sql", "algorithms"]
    difficulty: Level

class ManagerTurn(_TurnBase):
    """Ход менеджера: оценка предыдущего ответа кандидата и следующий вопрос о процессах разработки."""
    agent_type: Literal["manager"] = "manager"
    topic: Literal["agile", "processes", "planning", "metrics"]

class Score(BaseModel):
    name:str
# тут что-то еще для агента-аналитика по фидбеку
# учитывайте кто будет делать аналитика, что пока что не стал выделять отдельного оценщикаответов
# поэтому каждый шаг агента это оценка предыдущего ответа + следующий вопрос, те надо в аналитика втюхать еще 
# оценку последнего ответа, насчет отдельного агента для оценки вопрос насущный думаю после мвп можно сделать 
# щас только токены тратить имхо 
