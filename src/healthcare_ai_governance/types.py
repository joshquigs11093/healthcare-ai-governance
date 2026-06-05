"""Shared type aliases and exceptions used across components.

Per .spec §5, no untyped dictionaries cross module boundaries. The shared
``Literal`` enums live here; concrete Pydantic models live in each component's
``schema.py``.
"""

from __future__ import annotations

from typing import Literal

# --- Inventory enums (.spec §5.1) ---
RiskTier = Literal["low", "medium", "high", "critical"]
LifecycleStage = Literal[
    "proposed",
    "development",
    "validation",
    "production",
    "deprecated",
    "retired",
]
SystemType = Literal[
    "predictive",
    "generative",
    "decision_support",
    "operational",
    "research",
]
FDASamdClass = Literal["I", "II", "III", "IV", "not_applicable"]

# --- Risk assessment enums (.spec §5.3) ---
Likelihood = Literal["rare", "unlikely", "possible", "likely", "almost_certain"]
Severity = Literal["negligible", "minor", "moderate", "major", "catastrophic"]

# --- Fairness / audit enums (.spec §5.4) ---
DisparitySeverity = Literal["informational", "warning", "critical"]
FindingSeverity = Literal["info", "warning", "error", "critical"]

# Canonical ordering for tier comparisons (used by risk scoring, queries, UI).
RISK_TIER_ORDER: dict[RiskTier, int] = {
    "low": 0,
    "medium": 1,
    "high": 2,
    "critical": 3,
}
RISK_TIERS: tuple[RiskTier, ...] = ("low", "medium", "high", "critical")


class GovernanceError(Exception):
    """Base class for all toolkit errors."""


class InventoryValidationError(GovernanceError):
    """Raised when an inventory YAML file fails schema validation.

    Carries the offending file path (and optionally a line number) so the CLI
    and dashboard can point reviewers straight at the problem.
    """

    def __init__(self, message: str, *, path: str | None = None, line: int | None = None) -> None:
        self.path = path
        self.line = line
        location = ""
        if path is not None:
            location = f" [{path}{f':{line}' if line is not None else ''}]"
        super().__init__(f"{message}{location}")
