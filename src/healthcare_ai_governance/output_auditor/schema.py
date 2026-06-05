"""Output auditor schemas (.spec §5.4, §6.5)."""

from __future__ import annotations

from datetime import date
from typing import Protocol, runtime_checkable

from pydantic import BaseModel, Field

from healthcare_ai_governance.types import FindingSeverity


class LLMOutput(BaseModel):
    """A single LLM output to audit, with optional grounding context."""

    id: str
    text: str
    context: list[str] = Field(
        default_factory=list,
        description="Retrieved sources used to generate the output (for grounding checks).",
    )


class AuditFinding(BaseModel):
    """A single finding from one check on one output (.spec §5.4)."""

    check_name: str
    severity: FindingSeverity
    output_id: str
    excerpt: str  # Redacted if PHI detected
    explanation: str


class AuditReport(BaseModel):
    """The result of auditing a batch of outputs (.spec §5.4)."""

    system_id: str
    audit_date: date
    n_outputs_audited: int
    checks_run: list[str]
    findings: dict[str, list[AuditFinding]]
    overall_pass: bool


class AuditConfig(BaseModel):
    """Per-system audit configuration (.spec §6.5)."""

    model_config = {"extra": "forbid"}

    system_id: str = "unknown"
    enabled_checks: list[str] = Field(
        default_factory=lambda: [
            "phi_leakage",
            "unsupported_claims",
            "jailbreak",
            "tone",
            "citation_validity",
        ]
    )
    # phi_leakage: organization-specific MRN / account patterns (regex).
    mrn_patterns: list[str] = Field(default_factory=list)
    account_patterns: list[str] = Field(default_factory=list)
    # tone: phrases that violate the system's documented scope.
    prohibited_tone_patterns: list[str] = Field(default_factory=list)
    # Severity at or above which the CI gate fails.
    fail_on: FindingSeverity = "critical"
    # Whether LLM-as-judge checks may call out to a provider (else they no-op).
    use_llm_judge: bool = True


@runtime_checkable
class Check(Protocol):
    """A single audit check (.spec §6.5)."""

    name: str
    severity_on_match: FindingSeverity

    def evaluate(self, output: LLMOutput) -> list[AuditFinding]: ...
