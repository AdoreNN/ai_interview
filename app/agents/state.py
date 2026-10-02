from typing import Literal, TypedDict

# одно диалогове сообщение
class Message(TypedDict):
    role: Literal["user", "assistant"]
    content: str

# общий стейт дял агентов
class InterviewState(TypedDict, total=False):
    # настройки
    session_id: str
    target_position: str
    experience_level: str

    # диалоговый стаф
    messages: list[Message]
    current_question: str | None
    last_user_answer: str | None

    # резюме
    resume_topics: list[str]
    resume_experience: dict[str, int]

    # счетчики для рутирнга
    hr_count: int
    tech_count: int
    manager_count: int
    max_hr: int
    max_tech: int
    max_manager: int

    skills: dict[str, list[int]] # оценки по каждым аспектам ({"hr.teamwork": [7], "tech.async": [6]} и тд)
    pending_skill: str | None # ключ навыка(топика) текущего вопроса
    asked_topics: list[str] #спрошенные темы
    weaknesses: list[str] # слабости юзера, найденные агентами
    evaluation_log: list[dict] # skills с объяснениями по _TurnBase

    # финал собеса
    final_feedback: dict | None
    finished: bool
