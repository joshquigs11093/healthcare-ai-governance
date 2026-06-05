"""Pure, testable logic backing the Streamlit dashboard (.spec §6.6).

Kept out of the ``ui`` package so it is exercised by the test suite and counts
toward the non-UI coverage target. The Streamlit pages should contain only
presentation glue and call into here for anything with logic.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from healthcare_ai_governance.inventory.queries import CURRENCY_WINDOW, compliance_status
from healthcare_ai_governance.inventory.schema import AISystem
from healthcare_ai_governance.types import (
    RISK_TIERS,
    LifecycleStage,
    RiskTier,
)

# Artifact columns shown on the compliance matrix, in display order.
_COMPLIANCE_COLUMNS = (
    ("model_card", "Model Card"),
    ("risk_assessment", "Risk Assessment"),
    ("fairness_report", "Fairness Report"),
    ("audit_report", "Recent Audit"),
)

# Lifecycle stages shown (in order) on the risk-distribution heatmap.
_LIFECYCLE_ORDER: tuple[LifecycleStage, ...] = (
    "proposed",
    "development",
    "validation",
    "production",
    "deprecated",
    "retired",
)

# A review is "due soon" within this many days of its due date.
_DUE_SOON_DAYS = 30


@dataclass(frozen=True)
class ActivityEntry:
    """One line of version-control history for the activity feed."""

    timestamp: str
    author: str
    subject: str


def parse_git_log(output: str) -> list[ActivityEntry]:
    """Parse ``git log --format=%ai%x09%an%x09%s`` (tab-separated) output."""
    entries: list[ActivityEntry] = []
    for line in output.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t", 2)
        if len(parts) != 3:
            continue
        timestamp, author, subject = parts
        entries.append(ActivityEntry(timestamp.strip(), author.strip(), subject.strip()))
    return entries


def git_activity(repo_root: Path, n: int = 10, path: str = "inventory") -> list[ActivityEntry]:
    """Return the last ``n`` commits touching ``path`` as an audit trail.

    Returns an empty list if git is unavailable or the directory is not a
    repository (e.g. a tarball download) — the dashboard degrades gracefully
    rather than erroring.
    """
    try:
        result = subprocess.run(
            ["git", "log", f"-{n}", "--format=%ai%x09%an%x09%s", "--", path],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return []
    if result.returncode != 0:
        return []
    return parse_git_log(result.stdout)


def _months_between(earlier: date, later: date) -> int:
    return (later.year - earlier.year) * 12 + (later.month - earlier.month)


def recommended_actions(system: AISystem, as_of: date) -> list[str]:
    """Plain-language recommended actions for a system's detail page.

    Deterministic and ordered most- to least-urgent so the UI can show them as a
    prioritized checklist.
    """
    actions: list[str] = []
    la = system.linked_artifacts
    active = system.lifecycle_stage in {"production", "validation"}

    # Review timing.
    if system.next_review_due is not None and active:
        if system.next_review_due < as_of:
            actions.append(f"Review overdue since {system.next_review_due}.")
        elif (system.next_review_due - as_of).days <= _DUE_SOON_DAYS:
            actions.append(f"Review due soon ({system.next_review_due}).")
    if system.last_review is not None and (as_of - system.last_review) > CURRENCY_WINDOW:
        months = _months_between(system.last_review, as_of)
        actions.append(f"Last review was {months} months ago; artifacts may be stale.")

    # Artifact gaps (only flagged for active systems where they matter).
    if active:
        if la.model_card is None:
            actions.append("No model card linked.")
        if la.risk_assessment is None:
            actions.append("No risk assessment on file.")
        if system.is_generative and not la.audit_reports:
            actions.append("Generative system has no output audit on file.")

    # FDA-specific.
    if system.fda_samd_class != "not_applicable" and not system.fda_pccp_in_place:
        actions.append(
            f"FDA SaMD Class {system.fda_samd_class} without a Predetermined "
            f"Change Control Plan (PCCP)."
        )

    return actions


def _cell_label(present: bool, current: bool) -> str:
    if present and current:
        return "current"
    if present:
        return "stale"
    return "missing"


def compliance_rows(systems: list[AISystem], as_of: date | None = None) -> list[dict[str, str]]:
    """Flatten compliance status into display rows for the matrix and CSV export.

    Each row is ``{"ID": ..., "Name": ..., "<Artifact>": "current|stale|missing"}``.
    """
    status = compliance_status(systems, as_of=as_of)
    rows: list[dict[str, str]] = []
    for s in systems:
        st = status[s.id]
        row: dict[str, str] = {"ID": s.id, "Name": s.name}
        for key, label in _COMPLIANCE_COLUMNS:
            row[label] = _cell_label(st[f"{key}_present"], st[f"{key}_current"])
        rows.append(row)
    return rows


def risk_lifecycle_matrix(
    systems: list[AISystem],
) -> tuple[list[LifecycleStage], list[RiskTier], list[list[int]]]:
    """Build a (lifecycle x risk-tier) count matrix for the risk heatmap.

    Returns ``(row_labels, col_labels, matrix)`` where only lifecycle stages with
    at least one system are included as rows; tiers are always all four columns.
    """
    counts: dict[tuple[LifecycleStage, RiskTier], int] = {}
    present_stages: set[LifecycleStage] = set()
    for s in systems:
        counts[(s.lifecycle_stage, s.risk_tier)] = (
            counts.get((s.lifecycle_stage, s.risk_tier), 0) + 1
        )
        present_stages.add(s.lifecycle_stage)

    rows = [stage for stage in _LIFECYCLE_ORDER if stage in present_stages]
    cols = list(RISK_TIERS)
    matrix = [[counts.get((stage, tier), 0) for tier in cols] for stage in rows]
    return rows, cols, matrix
