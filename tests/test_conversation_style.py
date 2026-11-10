import pytest

from app.agents.nodes import base
from app.agents.prompts.hr import HR_SYSTEM_PROMPT
from app.agents.prompts.manager import MANAGER_SYSTEM_PROMPT
from app.agents.prompts.tech import TECH_SYSTEM_PROMPT
from app.agents.schemas.outputs import StageEval, TechTurn


def state(**overrides) -> dict:
    data = {
        "messages": [
            {"role": "assistant", "content": "Как вы ищете медленный запрос?"},
            {"role": "user", "content": "Смотрю EXPLAIN ANALYZE и индексы."},
        ],
        "pending_skill": "tech.sql",
        "hr_count": 2, "max_hr": 2,
        "tech_count": 1, "max_tech": 3,
        "manager_count": 0, "max_manager": 2,
    }
    data.update(overrides)
    return data


@pytest.fixture
def fake_llm(monkeypatch):
    seen = {}

    def install(result):
        def fake(schema, messages, is_valid=lambda _: True):
            seen["prompt"] = messages[0].content
            return result
        monkeypatch.setattr(base, "_invoke_structured", fake)
        return seen

    return install


def tech_turn(reaction: str) -> TechTurn:
    return TechTurn(
        reason="Назвал инструменты.", evaluation=6, weakness=None,
        reaction=reaction, question="А как читать план запроса?",
        topic="sql", difficulty="junior",
    )


def run_tech(s: dict) -> dict:
    return base.run_turn(
        s, agent="tech", schema=TechTurn, prompt_template=TECH_SYSTEM_PROMPT,
        count_key="tech_count", max_key="max_tech",
    )


def test_reaction_is_said_before_the_question(fake_llm):
    fake_llm(tech_turn("Ага, понятно."))
    result = run_tech(state())
    assert result["messages"][-1] == {
        "role": "assistant",
        "content": "Ага, понятно. А как читать план запроса?",
    }
    assert result["current_question"] == "А как читать план запроса?"


def test_empty_reaction_leaves_only_the_question(fake_llm):
    fake_llm(tech_turn("  "))
    assert run_tech(state())["messages"][-1]["content"] == "А как читать план запроса?"


def test_stage_close_hands_over_to_next_stage(fake_llm):
    seen = fake_llm(StageEval(reason="ok", evaluation=7, reaction="Понятно, дальше продолжит коллега."))
    result = run_tech(state(tech_count=3))
    assert "продолжит коллега" in seen["prompt"]
    assert "заверши интервью" not in seen["prompt"]
    assert result["messages"][-1]["content"] == "Понятно, дальше продолжит коллега."
    assert result["current_question"] is None and result["pending_skill"] is None


def test_last_stage_close_ends_the_interview(fake_llm):
    seen = fake_llm(StageEval(reason="ok", evaluation=7, reaction="Спасибо, разбор ниже."))
    run_tech(state(tech_count=3, manager_count=2))
    assert "заверши интервью" in seen["prompt"]


def test_stage_close_without_reaction_adds_no_message(fake_llm):
    fake_llm(StageEval(reason="ok", evaluation=7))
    result = run_tech(state(tech_count=3))
    assert "messages" not in result


def test_prompts_allow_natural_feedback():
    for prompt in (HR_SYSTEM_PROMPT, TECH_SYSTEM_PROMPT, MANAGER_SYSTEM_PROMPT):
        assert "Никогда не хвали" not in prompt
        assert "КАК ГОВОРИТЬ" in prompt


def test_retry_tells_the_model_what_was_wrong(monkeypatch):
    calls = []
    missing_eval = tech_turn("Хороший пример.").model_copy(update={"evaluation": None})

    class FakeStructured:
        def invoke(self, messages):
            calls.append(messages)
            return missing_eval if len(calls) == 1 else tech_turn("Хороший пример.")

    class FakeLLM:
        def with_structured_output(self, schema):
            return FakeStructured()

    monkeypatch.setattr(base, "get_llm", lambda: FakeLLM())
    result = base._invoke_structured(
        TechTurn, [object()], is_valid=lambda t: t.evaluation is not None
    )

    assert result.evaluation == 6
    assert len(calls) == 2
    assert calls[1][-1].content == base.RETRY_HINT


def test_questions_inside_reaction_are_not_duplicated():
    reply = base._compose_reply(
        "Понятно, вы знаете базовые приёмы. А как вы планируете задачи? Какие инструменты?",
        "Как вы планируете задачи?",
    )
    assert reply == "Понятно, вы знаете базовые приёмы. Как вы планируете задачи?"
    assert base._compose_reply("Что мотивирует?", "Что мотивирует?") == "Что мотивирует?"


def test_new_stage_starts_with_intro_instead_of_continuing_colleague(fake_llm):
    seen = fake_llm(tech_turn("Понятно. Я технический интервьюер."))
    s = state(tech_count=0, pending_skill=None)
    run_tech(s)
    assert "НАЧИНАЕШЬ НОВЫЙ ЭТАП" in seen["prompt"]
    assert "Не продолжай тему коллеги" in seen["prompt"]


def test_stage_start_note_only_on_first_turn_of_a_stage():
    assert base._stage_start_note({"messages": [], "tech_count": 0}, "tech_count") == ""
    assert base._stage_start_note(state(tech_count=1), "tech_count") == ""
    after_farewell = state(tech_count=0, messages=[{"role": "assistant", "content": "Спасибо, дальше коллега."}])
    assert "просто представься" in base._stage_start_note(after_farewell, "tech_count")


def test_history_ending_with_interviewer_reply_still_ends_with_user_message():
    s = state(tech_count=0, messages=[
        {"role": "user", "content": "Ответ"},
        {"role": "assistant", "content": "Спасибо, дальше продолжит коллега."},
    ])
    messages = base._to_lc_messages(s, "system")
    assert messages[-1].type == "human"
    assert base._to_lc_messages(state(), "system")[-1].content == "Смотрю EXPLAIN ANALYZE и индексы."


def test_last_stage_always_says_goodbye(fake_llm):
    fake_llm(StageEval(reason="ok", evaluation=7))
    result = run_tech(state(tech_count=3, manager_count=2))
    assert result["messages"][-1] == {"role": "assistant", "content": base.FINAL_FAREWELL}
