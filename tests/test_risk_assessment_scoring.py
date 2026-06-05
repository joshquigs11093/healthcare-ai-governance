"""Tests for deterministic risk scoring (.spec §6.3, §9).

Scoring is tested with small synthetic questionnaires for precise control over
the score ratio, plus a few integration checks against the bundled questionnaire.
"""

from __future__ import annotations

import pytest

from healthcare_ai_governance.risk_assessment.questionnaire import (
    SCREENING_QUESTION_ID,
    default_questionnaire,
)
from healthcare_ai_governance.risk_assessment.schema import RiskQuestion
from healthcare_ai_governance.risk_assessment.scoring import compute_risk_tier


def _scale_q(qid: str = "q1", weight: int = 1) -> RiskQuestion:
    return RiskQuestion(
        id=qid,
        category="model",
        nist_rmf_subcategory="MEASURE 2.3",
        text="scale",
        help_text="",
        response_type="scale_1_5",
        weight=weight,
    )


@pytest.mark.parametrize(
    ("value", "expected"),
    [(1, "low"), (2, "medium"), (3, "high"), (5, "critical")],
)
def test_score_maps_to_tier(value: int, expected: str) -> None:
    tier, _ = compute_risk_tier({"q1": value}, [_scale_q()])
    assert tier == expected


def test_tier_override_forces_floor() -> None:
    q_override = RiskQuestion(
        id="autonomy",
        category="use_case",
        nist_rmf_subcategory="MANAGE 1.3",
        text="autonomous?",
        help_text="",
        response_type="yes_no",
        weight=1,
        tier_overrides={"yes": "critical"},
    )
    # Score alone would be 'low' (scale=1), but the override forces critical.
    tier, rationale = compute_risk_tier({"q1": 1, "autonomy": "yes"}, [_scale_q(), q_override])
    assert tier == "critical"
    assert any("forced minimum tier to critical" in line for line in rationale)


def test_override_only_raises_never_lowers() -> None:
    q_override = RiskQuestion(
        id="floor",
        category="use_case",
        nist_rmf_subcategory="MAP 1.1",
        text="floor",
        help_text="",
        response_type="yes_no",
        weight=1,
        tier_overrides={"yes": "medium"},
    )
    # Score alone is 'critical' (scale=5); a 'medium' floor must not lower it.
    tier, _ = compute_risk_tier({"q1": 5, "floor": "yes"}, [_scale_q(), q_override])
    assert tier == "critical"


def test_unanswered_questions_ignored() -> None:
    tier, rationale = compute_risk_tier({}, [_scale_q()])
    assert tier == "low"
    assert "0/0" in " ".join(rationale)


def test_multiselect_and_text_scoring() -> None:
    multi = RiskQuestion(
        id="m",
        category="data",
        nist_rmf_subcategory="MAP 4.1",
        text="select all that apply",
        help_text="",
        response_type="multiselect",
        options=["a", "b", "c", "d"],
        weight=1,
    )
    free = RiskQuestion(
        id="t",
        category="data",
        nist_rmf_subcategory="MAP 4.2",
        text="notes",
        help_text="",
        response_type="text",
        weight=1,
    )
    # multiselect: 4/4 selected -> ratio 1.0; text contributes 0/0 (ignored).
    tier, rationale = compute_risk_tier(
        {"m": ["a", "b", "c", "d"], "t": "free text here"}, [multi, free]
    )
    assert tier == "critical"
    assert "4/4" in " ".join(rationale)

    # Two of four selected -> ratio 0.5 -> medium.
    tier2, _ = compute_risk_tier({"m": ["a", "b"]}, [multi, free])
    assert tier2 == "medium"


def _screening_q(answer_yes: bool) -> tuple[RiskQuestion, dict]:
    q = RiskQuestion(
        id=SCREENING_QUESTION_ID,
        category="model",
        nist_rmf_subcategory="MAP 1.1",
        text="generative?",
        help_text="",
        response_type="yes_no",
        weight=1,
    )
    return q, {SCREENING_QUESTION_ID: "yes" if answer_yes else "no"}


def test_generative_only_question_excluded_when_not_generative() -> None:
    gen_q = RiskQuestion(
        id="gen.x",
        category="model",
        nist_rmf_subcategory="MEASURE 2.3 (GAI)",
        text="gen risk",
        help_text="",
        response_type="scale_1_5",
        weight=1,
        generative_only=True,
    )
    screen, base = _screening_q(answer_yes=False)
    # gen.x answered 5 (max risk) but should be ignored since not generative.
    tier, _ = compute_risk_tier({**base, "gen.x": 5}, [screen, gen_q])
    assert tier == "low"


def test_generative_only_question_counted_when_generative() -> None:
    gen_q = RiskQuestion(
        id="gen.x",
        category="model",
        nist_rmf_subcategory="MEASURE 2.3 (GAI)",
        text="gen risk",
        help_text="",
        response_type="scale_1_5",
        weight=1,
        generative_only=True,
    )
    screen, base = _screening_q(answer_yes=True)
    # screening yes_no scores 1/1, gen.x scores 5/5 -> ratio 6/6 = 1.0 -> critical.
    tier, _ = compute_risk_tier({**base, "gen.x": 5}, [screen, gen_q])
    assert tier == "critical"


# ---- Integration against the bundled questionnaire ----


def test_bundled_questionnaire_autonomy_forces_critical() -> None:
    q = list(default_questionnaire())
    tier, _ = compute_risk_tier({"use_case.autonomy": "yes"}, q)
    assert tier == "critical"


def test_bundled_questionnaire_safest_answers_are_low() -> None:
    q = list(default_questionnaire())
    # Choose the lowest-risk option for every question.
    responses: dict = {}
    for question in q:
        if question.response_type == "select":
            responses[question.id] = question.options[0]
        elif question.response_type == "yes_no":
            responses[question.id] = "no"
        elif question.response_type == "scale_1_5":
            responses[question.id] = 1
    tier, _ = compute_risk_tier(responses, q)
    assert tier == "low"
