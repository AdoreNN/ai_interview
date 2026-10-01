import logging
from typing import Any
from langchain_core.exceptions import OutputParserException
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from pydantic import BaseModel, ValidationError
from app.agents.llm import get_llm
from app.agents.schemas.outputs import StageEval
from collections.abc import Callable
from app.agents.state import InterviewState

logger = logging.getLogger(__name__)
MAX_RETRIES = 2

class LLMOutputError(RuntimeError):
    """LLM не вернула валидный структурированный ответ."""

# конверт в ленгчейн формат
def _to_lc_messages(state: InterviewState, system_prompt: str) -> list[BaseMessage]:
    result: list[BaseMessage] = [SystemMessage(content=system_prompt)]
    history = state.get("messages", [])
    for m in history:
        cls = HumanMessage if m["role"] == "user" else AIMessage
        result.append(cls(content=m["content"]))
    if not history:
        result.append(HumanMessage(content="Начни собеседование. Задай первый вопрос."))
    return result

# вызов ллмки
def _invoke_structured(schema: type[BaseModel], messages: list[BaseMessage], is_valid: Callable[[Any], bool] = lambda _: True) -> Any:
    llm = get_llm().with_structured_output(schema)
    last_error: Exception | None = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            result = llm.invoke(messages)
            if result is not None and is_valid(result):
                return result
            logger.warning("Rejected LLM output (attempt %s): %s", attempt + 1, result)
        except (ValidationError, OutputParserException) as e:
            last_error = e
            logger.warning("Invalid LLM output (attempt %s): %s", attempt + 1, e)
    raise LLMOutputError(f"LLM не вернула валидный {schema.__name__}") from last_error


def _build_prompt(state: InterviewState, template: str, count_key: str, max_key: str) -> str:
    count = state.get(count_key, 0)
    max_questions = state.get(max_key, 1)
    return template.format(
        target_position=state.get("target_position", "Python developer"),
        experience_level=state.get("experience_level", "junior"),
        question_number=min(count + 1, max_questions),
        max_questions=max_questions,
        stage_first="да" if count == 0 else "нет",
        asked_topics=", ".join(state.get("asked_topics", [])) or "нет",
        resume_topics=", ".join(state.get("resume_topics", [])) or "нет данных",
    )


def _record_eval(state: InterviewState, turn: Any) -> dict:
    """Кладёт оценку в корзину pending_skill, слабость в weaknesses."""
    skills = {k: list(v) for k, v in state.get("skills", {}).items()}
    log = list(state.get("evaluation_log", []))
    weaknesses = list(state.get("weaknesses", []))
    pending = state.get("pending_skill")
    if turn.evaluation is not None and pending:
        skills.setdefault(pending, []).append(turn.evaluation)
        log.append({"skill": pending, "score": turn.evaluation, "reason": turn.reason})
    if turn.weakness:
        weaknesses.append(turn.weakness)
    return {"skills": skills, "evaluation_log": log, "weaknesses": weaknesses}


def _close_stage(state: InterviewState, prompt: str) -> dict:
    """Оценить последний ответ этапа без нового вопроса."""
    prompt += (
        "\n\nЭто был ПОСЛЕДНИЙ вопрос твоего этапа. Новый вопрос НЕ задавай: "
        "только оцени последний ответ кандидата."
    )
    turn = _invoke_structured(
        StageEval,
        _to_lc_messages(state, prompt),
        is_valid=lambda t: t.evaluation is not None,
    )
    return {
        **_record_eval(state, turn),
        "pending_skill": None,
        "current_question": None,
        "last_user_answer": None,
    }

# общая схема вызова ноды для каждого агента 
def run_turn(
    state: InterviewState,
    *,
    agent: str,
    schema: type[BaseModel],
    prompt_template: str,
    count_key: str,
    max_key: str,
) -> dict:
    """Один ход интервьюера: оценить прошлый ответ + задать следующий вопрос или."""
    count = state.get(count_key, 0)
    prompt = _build_prompt(state, prompt_template, count_key, max_key)
    if count>=state.get(max_key, 1):
        return _close_stage(state, prompt)
    
    history = state.get("messages", [])
    needs_eval = bool(state.get("pending_skill")) and bool(history) and history[-1]["role"] == "user"

    turn = _invoke_structured(schema, _to_lc_messages(state, prompt), is_valid=lambda t: not needs_eval or t.evaluation is not None)
    skill_key = f"{agent}.{turn.topic}"
    return {
        **_record_eval(state, turn),
        "messages": [
            *state.get("messages", []),
            {"role": "assistant", "content": turn.question},
        ],
        "current_question": turn.question,
        "last_user_answer": None,
        count_key: count + 1,
        "asked_topics": [*state.get("asked_topics", []), skill_key],
        "pending_skill": skill_key,
    }