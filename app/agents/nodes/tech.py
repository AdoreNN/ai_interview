# nodes/tech.py
from app.agents.nodes.base import run_turn
from app.agents.prompts.tech import TECH_SYSTEM_PROMPT
from app.agents.schemas.outputs import TechTurn
from app.agents.state import InterviewState

def run(state: InterviewState) -> dict:
    return run_turn(
        state,
        agent="tech",
        schema=TechTurn,
        prompt_template=TECH_SYSTEM_PROMPT,
        count_key="tech_count",
        max_key="max_tech",
    )