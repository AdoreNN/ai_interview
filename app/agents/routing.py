from langgraph.graph import END

from app.agents.state import InterviewState

STAGES = [
    ("hr", "hr_count", "max_hr"),
    ("tech", "tech_count", "max_tech"),
    ("manager", "manager_count", "max_manager"),
]


def route_next(state: InterviewState) -> str:
    if state.get("finished"):
        return "analytics"

    # есть неоценённый ответ, те penfing_skill : его оценивает автор вопроса
    pending = state.get("pending_skill")
    if pending:
        return pending.split(".")[0]

    for name, count_key, max_key in STAGES:
        if state.get(count_key, 0) < state.get(max_key, 0):
            return name
    return "analytics"


def after_node(state: InterviewState) -> str:
    """Вопрос задан: ждём пользователя. Иначе идём дальше."""
    return END if state.get("pending_skill") else route_next(state)