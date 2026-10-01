from app.agents.state import InterviewState
# прост заглушка для графа, нет смысловой нагрузки вообще

def run(state: InterviewState) -> dict:
    skills = state.get("skills", {})
    averages = {k: sum(v) / len(v) for k, v in skills.items() if v}
    return {
        "final_feedback": {"skill_averages": averages, "weaknesses": state.get("weaknesses", [])},
        "finished": True,
        "pending_skill": None,
        "current_question": None,
    }