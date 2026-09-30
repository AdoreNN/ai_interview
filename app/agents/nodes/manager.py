# nodes/manager.py
from app.agents.nodes.base import run_turn
from app.agents.prompts.manager import MANAGER_SYSTEM_PROMPT
from app.agents.schemas.outputs import ManagerTurn
from app.agents.state import InterviewState

def run(state: InterviewState) -> dict:
    return run_turn(
        state,
        agent="manager",
        schema=ManagerTurn,
        prompt_template=MANAGER_SYSTEM_PROMPT,
        count_key="manager_count",
        max_key="max_manager",
    )