from collections import defaultdict
from app.schemas import Band, EvaluationEntry, InterviewData, SkillStat, Stats


MIN_SCORES_FOR_CONCLUSIONS = 3

BAND_LABELS: dict[str, str] = {
    "weak": "слабый",
    "basic": "базовый",
    "good": "хороший",
    "excellent": "отличный",
}


class EmptyInterviewError(ValueError):
    """В переданных данных нечего анализировать (нет ни ответов кандидата, ни оценок)"""


def band_for(score: float) -> Band:
    if score < 4:
        return "weak"
    if score < 7:
        return "basic"
    if score < 9:
        return "good"
    return "excellent"


def is_candidate(role: str) -> bool:
    return role == "user"


def collect_entries(data: InterviewData) -> list[EvaluationEntry]:
    if data.evaluation_log:
        return list(data.evaluation_log)
    entries: list[EvaluationEntry] = []
    for skill, scores in data.skills.items():
        for score in scores:
            if isinstance(score, int) and 0 <= score <= 10:
                entries.append(EvaluationEntry(skill=skill, score=score))
    return entries


def ensure_has_data(data: InterviewData) -> None:
    has_answers = any(is_candidate(m.role) and m.content.strip() for m in data.messages)
    if not has_answers and not collect_entries(data):
        raise EmptyInterviewError("Нет данных для анализа: ни ответов кандидата в messages, ни оценок в evaluation_log/skills")


def _split_skill(skill: str) -> tuple[str, str]:
    agent, sep, topic = skill.partition(".")
    return (agent, topic) if sep else ("general", skill)


def _mean(values: list[int]) -> float:
    return round(sum(values) / len(values), 1)


def compute_stats(data: InterviewData) -> Stats:
    entries = collect_entries(data)
    answered = sum(1 for m in data.messages if is_candidate(m.role) and m.content.strip())

    if not entries:
        return Stats(answered_questions=answered, is_preliminary=True)

    by_skill: dict[str, list[int]] = defaultdict(list)
    by_agent: dict[str, list[int]] = defaultdict(list)
    for e in entries:
        by_skill[e.skill].append(e.score)
        by_agent[_split_skill(e.skill)[0]].append(e.score)

    skills = []
    for skill, scores in by_skill.items():
        agent, topic = _split_skill(skill)
        skills.append(
            SkillStat(
                skill=skill, agent=agent, topic=topic,
                average=_mean(scores), count=len(scores), scores=scores,
            )
        )

    overall = _mean([e.score for e in entries])

    # лучшие/худшие темы: не больше двух с каждой стороны, без пересечений и только
    # если оценки действительно различаются (при равных оценках «лучшей» темы нет)
    ranked = sorted(skills, key=lambda s: s.average, reverse=True)
    n = min(2, len(ranked) // 2)
    top, bottom = ranked[0].average, ranked[-1].average
    strongest = [s.skill for s in ranked[:n] if s.average > bottom]
    weakest = [s.skill for s in reversed(ranked[-n:]) if s.average < top] if n else []

    band = band_for(overall)
    return Stats(
        answered_questions=answered,
        overall_score=overall,
        overall_band=band,
        overall_band_label=BAND_LABELS[band],
        is_preliminary=len(entries) < MIN_SCORES_FOR_CONCLUSIONS,
        by_agent={a: _mean(v) for a, v in by_agent.items()},
        skills=skills,
        strongest=strongest,
        weakest=weakest,
    )


def format_dialog(data: InterviewData, max_message_chars: int, max_total_chars: int) -> str:
    lines = []
    for m in data.messages:
        who = "Кандидат" if is_candidate(m.role) else "Интервьюер"
        text = m.content.strip()
        if len(text) > max_message_chars:
            text = text[:max_message_chars] + "…"
        lines.append(f"{who}: {text}")
    dialog = "\n".join(lines)
    if len(dialog) > max_total_chars:
        dialog = "[начало диалога опущено]\n" + dialog[-max_total_chars:]
    return dialog or "нет"
