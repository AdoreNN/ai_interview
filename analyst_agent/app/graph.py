"""
START -> compute_stats -> (mode == "feedback") -> write_feedback  -> END
                       -> (mode == "chat")     -> answer_question -> END
"""

import json
from typing import Literal, TypedDict

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph

from app import llm as llm_client
from app.config import get_settings
from app.prompts import CHAT_SYSTEM_PROMPT, FEEDBACK_SYSTEM_PROMPT
from app.schemas import ChatMessage, Feedback, InterviewData, Stats
from app.stats import collect_entries, compute_stats, ensure_has_data, format_dialog


class AnalystState(TypedDict, total=False):
    mode: Literal["feedback", "chat"]
    interview: InterviewData
    stats: Stats
    feedback: Feedback | None
    history: list[ChatMessage]
    question: str
    answer: str


def _dumps(obj) -> str:
    return json.dumps(obj, ensure_ascii=False)


def _context(state: AnalystState) -> dict[str, str]:
    """Общие плейсхолдеры для обоих промптов."""
    settings = get_settings()
    data = state["interview"]
    feedback = state.get("feedback")
    return {
        "target_position": data.target_position or "не указана",
        "experience_level": data.experience_level or "не указан",
        "resume_topics": ", ".join(data.resume_topics) or "нет данных",
        "stats": _dumps(state["stats"].model_dump()),
        "evaluation_log": _dumps([e.model_dump() for e in collect_entries(data)]) or "[]",
        "weaknesses": "; ".join(data.weaknesses) or "нет",
        "dialog": format_dialog(data, settings.max_message_chars, settings.max_dialog_chars),
        "feedback": _dumps(feedback.model_dump()) if feedback else "не передан",
    }


def compute_stats_node(state: AnalystState) -> dict:
    data = state["interview"]
    ensure_has_data(data)
    return {"stats": compute_stats(data)}


def write_feedback_node(state: AnalystState) -> dict:
    prompt = FEEDBACK_SYSTEM_PROMPT.format(**_context(state))
    feedback = llm_client.invoke_structured(
        Feedback,
        [SystemMessage(content=prompt), HumanMessage(content="Напиши итоговый фидбек кандидату.")],
        is_valid=lambda f: bool(f.summary.strip()) and len(f.recommendations) > 0,
        temperature=0.3,
    )
    return {"feedback": feedback}


def answer_question_node(state: AnalystState) -> dict:
    settings = get_settings()
    prompt = CHAT_SYSTEM_PROMPT.format(**_context(state))
    messages: list[BaseMessage] = [SystemMessage(content=prompt)]
    for m in state.get("history", [])[-settings.max_chat_history :]:
        messages.append(HumanMessage(content=m.content) if m.role == "user" else AIMessage(content=m.content))
    messages.append(HumanMessage(content=state["question"]))
    return {"answer": llm_client.invoke_text(messages, temperature=0.4)}


def route_mode(state: AnalystState) -> str:
    return "answer_question" if state.get("mode") == "chat" else "write_feedback"


def build_graph():
    g = StateGraph(AnalystState)
    g.add_node("compute_stats", compute_stats_node)
    g.add_node("write_feedback", write_feedback_node)
    g.add_node("answer_question", answer_question_node)

    g.add_edge(START, "compute_stats")
    g.add_conditional_edges("compute_stats", route_mode, ["write_feedback", "answer_question"])
    g.add_edge("write_feedback", END)
    g.add_edge("answer_question", END)
    return g.compile()


analyst_graph = build_graph()
