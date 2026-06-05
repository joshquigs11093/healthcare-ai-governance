"""Deterministic, pure query functions over a loaded inventory (.spec §6.1)."""

from __future__ import annotations

from datetime import date, timedelta

from healthcare_ai_governance.inventory.schema import AISystem
from healthcare_ai_governance.types import (
    RISK_TIERS,
    LifecycleStage,
    RiskTier,
)

# Artifacts are "current" if produced within this window (.spec §6.1, §6.6).
CURRENCY_WINDOW = timedelta(days=365)

# Lifecycle stages for which an overdue review actually matters.
_ACTIVE_STAGES: frozenset[LifecycleStage] = frozenset({"production", "validation"})

_ARTIFACT_KEYS = ("model_card", "risk_assessment", "fairness_report", "audit_report")


def systems_overdue_for_review(systems: list[AISystem], as_of: date) -> list[AISystem]:
    """Active systems whose ``next_review_due`` is before ``as_of``.

    Only production/validation systems count; a proposed or retired system being
    "overdue" is not actionable.
    """
    return [
        s
        for s in systems
        if s.lifecycle_stage in _ACTIVE_STAGES
        and s.next_review_due is not None
        and s.next_review_due < as_of
    ]


def systems_by_risk_tier(systems: list[AISystem]) -> dict[RiskTier, list[AISystem]]:
    """Group systems by risk tier. Every tier key is present (possibly empty)."""
    grouped: dict[RiskTier, list[AISystem]] = {tier: [] for tier in RISK_TIERS}
    for s in systems:
        grouped[s.risk_tier].append(s)
    return grouped


def compliance_status(
    systems: list[AISystem], as_of: date | None = None
) -> dict[str, dict[str, bool]]:
    """For each system id, which artifacts are present and which are current.

    Returns a nested mapping: ``{system_id: {"<artifact>_present": bool,
    "<artifact>_current": bool, ...}}``.

    "Current" requires a ``last_review`` within :data:`CURRENCY_WINDOW`. Presence
    is determined from the system's ``linked_artifacts``; recency is approximated
    from ``last_review`` because the inventory record, not the file mtime, is the
    auditable source of truth.
    """
    reference = as_of or date.today()
    result: dict[str, dict[str, bool]] = {}
    for s in systems:
        recent = s.last_review is not None and (reference - s.last_review) <= CURRENCY_WINDOW
        la = s.linked_artifacts
        present = {
            "model_card": la.model_card is not None,
            "risk_assessment": la.risk_assessment is not None,
            "fairness_report": la.fairness_report is not None,
            "audit_report": len(la.audit_reports) > 0,
        }
        status: dict[str, bool] = {}
        for key in _ARTIFACT_KEYS:
            status[f"{key}_present"] = present[key]
            status[f"{key}_current"] = present[key] and recent
        result[s.id] = status
    return result


def lifecycle_distribution(systems: list[AISystem]) -> dict[LifecycleStage, int]:
    """Count of systems in each lifecycle stage (only non-zero stages included)."""
    counts: dict[LifecycleStage, int] = {}
    for s in systems:
        counts[s.lifecycle_stage] = counts.get(s.lifecycle_stage, 0) + 1
    return counts
