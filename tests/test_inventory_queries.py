"""Tests for inventory query functions (.spec §9)."""

from __future__ import annotations

from datetime import date

from healthcare_ai_governance.inventory.queries import (
    compliance_status,
    lifecycle_distribution,
    systems_by_risk_tier,
    systems_overdue_for_review,
)


def test_overdue_only_active_stages(system_factory, today: date, days_ago) -> None:
    overdue_prod = system_factory(
        id="prod", lifecycle_stage="production", next_review_due=days_ago(1)
    )
    overdue_retired = system_factory(
        id="retired", lifecycle_stage="retired", next_review_due=days_ago(100)
    )
    not_due = system_factory(
        id="future", lifecycle_stage="production", next_review_due=date(2027, 1, 1)
    )
    no_date = system_factory(id="nodate", lifecycle_stage="validation", next_review_due=None)

    result = systems_overdue_for_review([overdue_prod, overdue_retired, not_due, no_date], today)
    assert [s.id for s in result] == ["prod"]


def test_by_risk_tier_has_all_keys(system_factory) -> None:
    grouped = systems_by_risk_tier([system_factory(id="a", risk_tier="high")])
    assert set(grouped) == {"low", "medium", "high", "critical"}
    assert [s.id for s in grouped["high"]] == ["a"]
    assert grouped["low"] == []


def test_lifecycle_distribution(system_factory) -> None:
    systems = [
        system_factory(id="a", lifecycle_stage="production"),
        system_factory(id="b", lifecycle_stage="production"),
        system_factory(id="c", lifecycle_stage="validation"),
    ]
    assert lifecycle_distribution(systems) == {"production": 2, "validation": 1}


def test_compliance_present_and_current(system_factory, today: date, days_ago) -> None:
    recent = system_factory(
        id="good",
        last_review=days_ago(30),
        linked_artifacts={"model_card": "artifacts/model_cards/good.md"},
    )
    status = compliance_status([recent], as_of=today)["good"]
    assert status["model_card_present"] is True
    assert status["model_card_current"] is True
    assert status["risk_assessment_present"] is False
    assert status["risk_assessment_current"] is False


def test_compliance_present_but_stale(system_factory, today: date, days_ago) -> None:
    stale = system_factory(
        id="stale",
        last_review=days_ago(400),
        linked_artifacts={"model_card": "artifacts/model_cards/stale.md"},
    )
    status = compliance_status([stale], as_of=today)["stale"]
    assert status["model_card_present"] is True
    assert status["model_card_current"] is False


def test_compliance_audit_reports_list(system_factory, today: date, days_ago) -> None:
    s = system_factory(
        id="aud",
        last_review=days_ago(10),
        linked_artifacts={"audit_reports": ["artifacts/audit_reports/aud-2026.json"]},
    )
    status = compliance_status([s], as_of=today)["aud"]
    assert status["audit_report_present"] is True
    assert status["audit_report_current"] is True
