"""Tests for dashboard support logic (.spec §6.6)."""

from __future__ import annotations

import subprocess
from datetime import date
from pathlib import Path

from healthcare_ai_governance.dashboard_support import (
    ActivityEntry,
    compliance_rows,
    git_activity,
    parse_git_log,
    recommended_actions,
    risk_lifecycle_matrix,
)


def test_parse_git_log() -> None:
    out = (
        "2026-06-01 10:00:00 -0600\tAlice\tAdd sepsis system\n"
        "2026-05-30 09:00:00 -0600\tBob\tUpdate readmission review\n"
        "\n"  # blank line ignored
        "malformed line without tabs\n"  # skipped
    )
    entries = parse_git_log(out)
    assert entries == [
        ActivityEntry("2026-06-01 10:00:00 -0600", "Alice", "Add sepsis system"),
        ActivityEntry("2026-05-30 09:00:00 -0600", "Bob", "Update readmission review"),
    ]


def test_git_activity_non_repo_returns_empty(tmp_path: Path) -> None:
    assert git_activity(tmp_path) == []


def test_git_activity_real_repo(tmp_path: Path) -> None:
    def run(*args: str) -> None:
        subprocess.run(args, cwd=tmp_path, check=True, capture_output=True)

    run("git", "init")
    run("git", "config", "user.email", "t@example.com")
    run("git", "config", "user.name", "Tester")
    (tmp_path / "inventory").mkdir()
    (tmp_path / "inventory" / "a.yaml").write_text("x: 1\n", encoding="utf-8")
    run("git", "add", "-A")
    run("git", "commit", "-m", "Seed inventory")

    entries = git_activity(tmp_path, n=5)
    assert len(entries) == 1
    assert entries[0].subject == "Seed inventory"
    assert entries[0].author == "Tester"


def test_recommended_actions_overdue_and_gaps(system_factory) -> None:
    s = system_factory(
        id="x",
        lifecycle_stage="production",
        next_review_due=date(2026, 1, 1),
        last_review=date(2024, 12, 1),
        linked_artifacts={},
    )
    actions = recommended_actions(s, as_of=date(2026, 6, 5))
    assert any("overdue" in a for a in actions)
    assert any("model card" in a for a in actions)
    assert any("risk assessment" in a for a in actions)


def test_recommended_actions_due_soon(system_factory) -> None:
    s = system_factory(
        id="x",
        lifecycle_stage="validation",
        next_review_due=date(2026, 6, 20),
        last_review=date(2026, 5, 1),
        linked_artifacts={
            "model_card": "m.md",
            "risk_assessment": "r.pdf",
        },
    )
    actions = recommended_actions(s, as_of=date(2026, 6, 5))
    assert any("due soon" in a for a in actions)


def test_recommended_actions_generative_needs_audit(system_factory) -> None:
    s = system_factory(
        id="g",
        lifecycle_stage="validation",
        is_generative=True,
        last_review=date(2026, 5, 1),
        linked_artifacts={"model_card": "m.md", "risk_assessment": "r.pdf"},
    )
    actions = recommended_actions(s, as_of=date(2026, 6, 5))
    assert any("output audit" in a for a in actions)


def test_recommended_actions_fda_without_pccp(system_factory) -> None:
    s = system_factory(
        id="rad",
        lifecycle_stage="validation",
        fda_samd_class="II",
        fda_pccp_in_place=False,
        last_review=date(2026, 5, 1),
        linked_artifacts={"model_card": "m.md", "risk_assessment": "r.pdf"},
    )
    actions = recommended_actions(s, as_of=date(2026, 6, 5))
    assert any("PCCP" in a for a in actions)


def test_recommended_actions_clean_system(system_factory) -> None:
    s = system_factory(
        id="ok",
        lifecycle_stage="production",
        next_review_due=date(2027, 1, 1),
        last_review=date(2026, 5, 1),
        linked_artifacts={"model_card": "m.md", "risk_assessment": "r.pdf"},
    )
    assert recommended_actions(s, as_of=date(2026, 6, 5)) == []


def test_recommended_actions_development_no_artifact_nags(system_factory) -> None:
    # Development-stage systems should not be nagged about missing artifacts.
    s = system_factory(id="dev", lifecycle_stage="development", linked_artifacts={})
    assert recommended_actions(s, as_of=date(2026, 6, 5)) == []


def test_compliance_rows(system_factory) -> None:
    systems = [
        system_factory(
            id="full",
            name="Full",
            last_review=date(2026, 5, 1),
            linked_artifacts={
                "model_card": "m.md",
                "risk_assessment": "r.pdf",
                "fairness_report": "f.html",
                "audit_reports": ["a.json"],
            },
        ),
        system_factory(
            id="stale",
            name="Stale",
            last_review=date(2024, 1, 1),
            linked_artifacts={"model_card": "m.md"},
        ),
        system_factory(id="empty", name="Empty", linked_artifacts={}),
    ]
    rows = compliance_rows(systems, as_of=date(2026, 6, 5))
    by_id = {r["ID"]: r for r in rows}
    assert by_id["full"]["Model Card"] == "current"
    assert by_id["full"]["Recent Audit"] == "current"
    assert by_id["stale"]["Model Card"] == "stale"
    assert by_id["empty"]["Risk Assessment"] == "missing"


def test_risk_lifecycle_matrix(system_factory) -> None:
    systems = [
        system_factory(id="a", lifecycle_stage="production", risk_tier="high"),
        system_factory(id="b", lifecycle_stage="production", risk_tier="high"),
        system_factory(id="c", lifecycle_stage="validation", risk_tier="medium"),
    ]
    rows, cols, matrix = risk_lifecycle_matrix(systems)
    assert cols == ["low", "medium", "high", "critical"]
    # Rows ordered by lifecycle order: validation before production.
    assert rows == ["validation", "production"]
    val_row = matrix[rows.index("validation")]
    prod_row = matrix[rows.index("production")]
    assert val_row[cols.index("medium")] == 1
    assert prod_row[cols.index("high")] == 2
