"""Deterministic risk tier computation (.spec §6.3).

Both the rules (``data/questionnaire.yaml``) and this algorithm are short and
explicit so a non-developer can audit how a tier was reached. The function
returns the tier together with human-readable rationale lines.
"""

from __future__ import annotations

from healthcare_ai_governance.risk_assessment.questionnaire import (
    applicable_questions,
    is_generative_response,
)
from healthcare_ai_governance.risk_assessment.schema import (
    ResponseValue,
    RiskQuestion,
)
from healthcare_ai_governance.types import RISK_TIER_ORDER, RISK_TIERS, RiskTier

# Score-ratio cut points mapping the weighted score to a tier (.spec §6.3).
_SCORE_TIER_CUTS: tuple[tuple[float, RiskTier], ...] = (
    (0.30, "low"),
    (0.55, "medium"),
    (0.80, "high"),
)


def _score_response(question: RiskQuestion, response: ResponseValue) -> int:
    """Risk contribution of a single response (see scoring convention in YAML)."""
    rt = question.response_type
    if rt == "yes_no":
        return 1 if str(response).strip().lower() == "yes" else 0
    if rt == "scale_1_5":
        try:
            value = int(response)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return 0
        return max(1, min(5, value))
    if rt == "select":
        if isinstance(response, str) and response in question.options:
            return question.options.index(response)
        return 0
    if rt == "multiselect":
        if isinstance(response, list):
            return len(response)
        return 0
    return 0  # text: not scored


def _max_response_score(question: RiskQuestion) -> int:
    rt = question.response_type
    if rt == "yes_no":
        return 1
    if rt == "scale_1_5":
        return 5
    if rt == "select":
        return max(0, len(question.options) - 1)
    if rt == "multiselect":
        return len(question.options)
    return 0  # text


def _tier_from_ratio(ratio: float) -> RiskTier:
    for threshold, tier in _SCORE_TIER_CUTS:
        if ratio < threshold:
            return tier
    return "critical"


def compute_risk_tier(
    responses: dict[str, ResponseValue],
    questionnaire: list[RiskQuestion],
) -> tuple[RiskTier, list[str]]:
    """Compute the risk tier from responses. Returns ``(tier, rationale_lines)``.

    Steps: (1) apply hard tier-override floors, (2) compute the weighted score
    over applicable questions, (3) map the score ratio to a tier, (4) take the
    maximum of the score-based tier and the override floor.
    """
    rationale: list[str] = []
    is_generative = is_generative_response(responses)
    questions = applicable_questions(questionnaire, is_generative=is_generative)

    # Step 1: tier overrides (hard floors).
    minimum_tier: RiskTier = "low"
    for question in questions:
        response = responses.get(question.id)
        if response is None:
            continue
        response_key = str(response) if not isinstance(response, list) else None
        if response_key and response_key in question.tier_overrides:
            override_tier = question.tier_overrides[response_key]
            if RISK_TIER_ORDER[override_tier] > RISK_TIER_ORDER[minimum_tier]:
                minimum_tier = override_tier
                rationale.append(
                    f"Question '{question.id}' response forced minimum tier "
                    f"to {override_tier} (NIST {question.nist_rmf_subcategory})"
                )

    # Step 2: weighted score over applicable questions.
    score = 0
    max_score = 0
    for question in questions:
        response = responses.get(question.id)
        if response is None:
            continue
        score += _score_response(question, response) * question.weight
        max_score += _max_response_score(question) * question.weight

    score_ratio = score / max_score if max_score > 0 else 0.0
    rationale.append(f"Weighted score: {score}/{max_score} = {score_ratio:.2f}")

    # Step 3: map score to tier.
    score_tier = _tier_from_ratio(score_ratio)
    rationale.append(f"Score-based tier: {score_tier}")

    # Step 4: maximum of score-based tier and the override floor.
    final_idx = max(RISK_TIER_ORDER[score_tier], RISK_TIER_ORDER[minimum_tier])
    final_tier = RISK_TIERS[final_idx]
    rationale.append(f"Final tier: {final_tier}")

    return final_tier, rationale
