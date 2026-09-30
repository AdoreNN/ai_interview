import sys

from app.agents.nodes import hr, manager, tech

AGENTS = {
    "hr": (hr, "hr_count", "max_hr"),
    "tech": (tech, "tech_count", "max_tech"),
    "manager": (manager, "manager_count", "max_manager"),
}


def main(name: str) -> None:
    module, count_key, max_key = AGENTS[name]
    state = {
        "target_position": "Python backend developer",
        "experience_level": "middle",
        "messages": [],
        "skills": {},
        "asked_topics": [],
        "weaknesses": [],
        "evaluation_log": [],
        "pending_skill": None,
        "max_hr": 3, "max_tech": 5, "max_manager": 2,
        "hr_count": 0, "tech_count": 0, "manager_count": 0,
    }

    while state[count_key] < state[max_key]:
        state.update(module.run(state))
        print(f"\nИНТЕРВЬЮЕР: {state['current_question']}")
        if state["evaluation_log"]:
            print(f"  [оценка прошлого ответа] {state['evaluation_log'][-1]}")

        answer = input("ВЫ: ").strip()
        if answer in {"q", "exit"}:
            break
        state["messages"].append({"role": "user", "content": answer})
        state["last_user_answer"] = answer

    print("\n--- ИТОГ ---")
    print("skills:", state["skills"])
    print("weaknesses:", state["weaknesses"])


if __name__ == "__main__":
    main(sys.argv[1])