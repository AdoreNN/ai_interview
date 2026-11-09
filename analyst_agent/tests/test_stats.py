import json
from pathlib import Path
import pytest
from app.schemas import InterviewData
from app.stats import EmptyInterviewError, band_for, compute_stats, ensure_has_data, format_dialog

SAMPLES = Path(__file__).resolve().parent.parent / "samples"


def load(name: str) -> InterviewData:
    return InterviewData.model_validate(json.loads((SAMPLES / name).read_text()))


def test_stats_sample():
    s = compute_stats(load("sample_state.json"))
    assert s.answered_questions == 6
    assert s.overall_score == 5.8  # (7+3+8+5+9+3)/6
    assert s.overall_band == "basic"
    assert s.by_agent == {"hr": 5.0, "tech": 7.3, "manager": 3.0}
    assert s.strongest == ["tech.decorators", "tech.async"]
    assert s.weakest == ["hr.conflict", "manager.planning"] or s.weakest == ["manager.planning", "hr.conflict"]
    assert not set(s.strongest) & set(s.weakest)


def test_typo_alias_is_accepted():
    assert load("sample_state.json").resume_experience == {"Python": 3, "PostgreSQL": 2}


def test_skills_fallback_when_no_log():
    data = InterviewData(skills={"tech.async": [8, 6], "hr.teamwork": [4]})
    s = compute_stats(data)
    assert s.overall_score == 6.0
    assert {x.skill: x.count for x in s.skills} == {"tech.async": 2, "hr.teamwork": 1}


def test_skill_without_dot():
    s = compute_stats(InterviewData(skills={"python": [6]}))
    assert s.skills[0].agent == "general" and s.skills[0].topic == "python"


def test_single_skill_has_no_strongest_weakest():
    s = compute_stats(InterviewData(skills={"tech.async": [8]}))
    assert s.strongest == [] and s.weakest == []


def test_no_scores_but_answers():
    data = InterviewData(messages=[{"role": "user", "content": "привет"}])
    s = compute_stats(data)
    assert s.overall_score is None and s.overall_band is None and s.answered_questions == 1


def test_empty_raises():
    with pytest.raises(EmptyInterviewError):
        ensure_has_data(InterviewData())
    with pytest.raises(EmptyInterviewError):
        ensure_has_data(InterviewData(messages=[{"role": "assistant", "content": "вопрос"}]))


@pytest.mark.parametrize("score,band", [(0, "weak"), (3.9, "weak"), (4, "basic"), (6.9, "basic"), (7, "good"), (8.9, "good"), (9, "excellent")])
def test_bands(score, band):
    assert band_for(score) == band


def test_format_dialog_truncation():
    data = InterviewData(messages=[{"role": "user", "content": "x" * 100}] * 10)
    short = format_dialog(data, max_message_chars=10, max_total_chars=10_000)
    assert "x" * 11 not in short and "…" in short
    capped = format_dialog(data, max_message_chars=100, max_total_chars=200)
    assert capped.startswith("[начало диалога опущено]")


def test_equal_scores_have_no_strongest_or_weakest():
    s = compute_stats(load("sample_state_weak.json"))
    assert s.overall_score == 0.0
    assert s.strongest == [] and s.weakest == []


def test_partial_ties_do_not_leak_into_strongest():
    s = compute_stats(InterviewData(skills={"a.x": [8], "a.y": [5], "a.z": [5], "a.w": [5]}))
    assert s.strongest == ["a.x"] # пятёрки не «сильные», хоть и попали в топ-2
    assert set(s.weakest) <= {"a.y", "a.z", "a.w"} and len(s.weakest) == 2


def test_preliminary_flag_and_russian_label():
    full = compute_stats(load("sample_state.json"))
    assert full.is_preliminary is False and full.overall_band_label == "базовый"
    short = compute_stats(load("sample_state_weak.json")) # всего 2 оценки
    assert short.is_preliminary is True and short.overall_band_label == "слабый"
    no_scores = compute_stats(InterviewData(messages=[{"role": "user", "content": "привет"}]))
    assert no_scores.is_preliminary is True and no_scores.overall_band_label is None
