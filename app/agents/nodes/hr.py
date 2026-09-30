# nodes/hr.py
from app.agents.nodes.base import run_turn
from app.agents.prompts.hr import HR_SYSTEM_PROMPT
from app.agents.schemas.outputs import HRTurn
from app.agents.state import InterviewState

def run(state: InterviewState) -> dict:
    return run_turn(
        state,
        agent="hr",
        schema=HRTurn,
        prompt_template=HR_SYSTEM_PROMPT,
        count_key="hr_count",
        max_key="max_hr",
    )