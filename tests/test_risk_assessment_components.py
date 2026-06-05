"""Tests for questionnaire loading, mitigations, and assessment building (.spec §6.3)."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from healthcare_ai_governance.risk_assessment.generator import (
    _assessment_signature,
    build_assessment,
    build_risk_register,
)
from healthcare_ai_governance.risk_assessment.mitigations import (
    default_mitigation_rules,
    recommend_mitigations,
)
from healthcare_ai_governance.risk_assessment.questionnaire import (
    default_questionnaire,
    load_questionnaire,
)
from healthcare_ai_governance.types import GovernanceError


def test_bundled_questionnaire_loads() -> None:
    q = default_questionnaire()
    assert len(q) >= 40
    # Every question carries a NIST subcategory.
    assert all(item.nist_rmf_subcategory for item in q)
    # The screening question is present.
    assert any(item.id == "model.is_generative" for item in q)


def test_questionnaire_rejects_duplicate_ids(tmp_path: Path) -> None:
    import yaml

    q = {
        "id": "a",
        "category": "model",
        "nist_rmf_subcategory": "X",
        "text": "t",
        "help_text": "h",
        "response_type": "yes_no",
    }
    bad = tmp_path / "q.yaml"
    bad.write_text(yaml.safe_dump({"questions": [q, dict(q)]}), encoding="utf-8")
    with pytest.raises(GovernanceError, match="Duplicate"):
        load_questionnaire(bad)


def test_questionnaire_missing_file() -> None:
    with pytest.raises(GovernanceError, match="not found"):
        load_questionnaire(Path("nope.yaml"))


def test_mitigations_fire_on_pattern() -> None:
    rules = list(default_mitigation_rules())
    responses = {
        "deployment.human_oversight": "no human oversight",
        "model.validation": "not yet validated",
    }
    out = recommend_mitigations(responses, "high", rules)
    assert any("human-in-the-loop" in m for m in out)
    assert any("external" in m.lower() for m in out)
    # All include a NIST tag.
    assert all("NIST" in m for m in out)


def test_mitigations_min_tier_gate() -> None:
    rules = list(default_mitigation_rules())
    # The escalate rule fires only at high+.
    low = recommend_mitigations({}, "low", rules)
    high = recommend_mitigations({}, "high", rules)
    assert not any("Escalate" in m for m in low)
    assert any("Escalate" in m for m in high)


def test_build_risk_register_thresholds() -> None:
    q = list(default_questionnaire())
    # High-risk answers should produce register entries; safe answers should not.
    risky = {"use_case.patient_safety": "serious potential for harm", "model.robustness": 5}
    register = build_risk_register(risky, q)
    assert register
    assert register[0].inherent_risk_score >= register[-1].inherent_risk_score  # sorted desc
    for item in register:
        assert 1 <= item.inherent_risk_score <= 25


def test_build_assessment_signature_is_tamper_evident() -> None:
    q = list(default_questionnaire())
    assessment = build_assessment(
        system_id="demo",
        assessor_name="Dr. Test",
        assessor_role="CMIO",
        assessment_date=date(2026, 6, 1),
        responses={"use_case.autonomy": "yes"},
        questionnaire=q,
    )
    assert assessment.computed_risk_tier == "critical"
    assert assessment.signature_hash
    # Recomputing the signature on the unchanged content matches.
    assert _assessment_signature(assessment) == assessment.signature_hash
    # Mutating content changes the signature.
    tampered = assessment.model_copy(update={"computed_risk_tier": "low"})
    assert _assessment_signature(tampered) != assessment.signature_hash
