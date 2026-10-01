import os
import sys

from app.agents.graph import interview_graph

DEBUG = os.getenv("DEBUG_EVAL") == "1"


def main(only: str | None) -> None:
    limits = {"hr": 3, "tech": 5, "manager": 2}
    if only:
        limits = {k: (v if k == only else 0) for k, v in limits.items()}

    state = {
        "target_position": "Python backend developer",
        "experience_level": "middle",
        "messages": [],
        "skills": {},
        "asked_topics": [],
        "weaknesses": [],
        "evaluation_log": [],
        "pending_skill": None,
        "finished": False,
        "hr_count": 0, "tech_count": 0, "manager_count": 0,
        "max_hr": limits["hr"], "max_tech": limits["tech"], "max_manager": limits["manager"],
    }

    while True:
        state = interview_graph.invoke(state)
        if state.get("finished"):
            break
        print(f"\nИНТЕРВЬЮЕР: {state['current_question']}")
        # if DEBUG and state["evaluation_log"]:
        #     print(f"  [оценка прошлого ответа] {state['evaluation_log'][-1]}")
        answer = ""
        while not answer:
            answer = input("ВЫ: ").strip()
        if answer in {"q", "exit"}:
            break
        state["messages"].append({"role": "user", "content": answer})
        state["last_user_answer"] = answer

    print("\n--- ИТОГ ---")
    print("skills:", state["skills"])
    print("weaknesses:", state["weaknesses"])
    if DEBUG:
        print("evaluation_log:", state["evaluation_log"])


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)