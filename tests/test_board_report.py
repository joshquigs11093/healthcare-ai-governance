"""Tests for the board report generator (.spec §6.6)."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from healthcare_ai_governance.board_report.generator import (
    build_board_report_data,
    generate_board_report_pdf,
    render_board_report_html,
)
from healthcare_ai_governance.inventory.schema import Organization
from healthcare_ai_governance.shared.pdf import pdf_available

_ORG = Organization(
    name="Test Health",
    type="integrated health system",
    governance_committee="AI Committee",
    ai_program_lead="Dr. Lead",
)
_TODAY = date(2026, 6, 5)


def _build(systems):  # type: ignore[no-untyped-def]
    return build_board_report_data(
        systems,
        _ORG,
        period_start=date(2026, 3, 1),
        period_end=_TODAY,
        generation_date=_TODAY,
    )


def test_counts_and_summary(system_factory) -> None:
    systems = [
        system_factory(id="a", risk_tier="critical", lifecycle_stage="production"),
        system_factory(id="b", risk_tier="high", lifecycle_stage="validation"),
        system_factory(id="c", risk_tier="low", lifecycle_stage="production"),
    ]
    data = _build(systems)
    assert data.total_systems == 3
    assert data.production_count == 2
    assert data.high_critical_count == 2
    assert "3 AI system" in data.executive_summary
    # Elevated systems sorted critical-first.
    assert data.elevated_systems[0].risk_tier == "critical"


def test_overdue_detection(system_factory) -> None:
    systems = [
        system_factory(
            id="late", lifecycle_stage="production", next_review_due=date(2026, 1, 1)
        ),
        system_factory(
            id="ok", lifecycle_stage="production", next_review_due=date(2027, 1, 1)
        ),
    ]
    data = _build(systems)
    assert data.overdue_count == 1
    assert data.overdue_systems[0].id == "late"


def test_recommendations_overdue_and_missing_ra(system_factory) -> None:
    systems = [
        system_factory(
            id="late",
            name="Late System",
            risk_tier="high",
            lifecycle_stage="production",
            next_review_due=date(2026, 1, 1),
            linked_artifacts={},
        ),
    ]
    data = _build(systems)
    joined = " ".join(data.recommendations)
    assert "overdue" in joined
    assert "risk assessment" in joined.lower()


def test_recommendations_clean_portfolio(system_factory) -> None:
    systems = [
        system_factory(
            id="ok",
            risk_tier="low",
            lifecycle_stage="production",
            next_review_due=date(2027, 1, 1),
        )
    ]
    data = _build(systems)
    assert any("No outstanding" in r for r in data.recommendations)


def test_render_html(system_factory) -> None:
    data = _build([system_factory(id="a", risk_tier="high", lifecycle_stage="production")])
    html = render_board_report_html(data, "Internal Use Only")
    assert "<html" in html.lower()
    assert "AI Governance Board Report" in html
    assert "Test Health" in html
    assert "@bottom-right" in html  # page-number footer


@pytest.mark.skipif(not pdf_available(), reason="WeasyPrint not available")
def test_generate_pdf(system_factory, tmp_path: Path) -> None:
    data = _build([system_factory(id="a")])
    out = generate_board_report_pdf(data, tmp_path / "board.pdf")
    assert out.read_bytes().startswith(b"%PDF")
