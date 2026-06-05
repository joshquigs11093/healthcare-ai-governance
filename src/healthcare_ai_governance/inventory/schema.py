"""Inventory Pydantic models (.spec §5.1)."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field, HttpUrl

from healthcare_ai_governance.types import (
    FDASamdClass,
    LifecycleStage,
    RiskTier,
    SystemType,
)


class LinkedArtifacts(BaseModel):
    """Relative paths (from repo root) to the artifacts produced for a system."""

    model_card: str | None = None
    risk_assessment: str | None = None
    fairness_report: str | None = None
    audit_reports: list[str] = Field(default_factory=list)
    monitoring_dashboard_url: HttpUrl | None = None
    runbook_url: HttpUrl | None = None


class AISystem(BaseModel):
    """A single AI/ML system tracked in the governance inventory."""

    model_config = {"extra": "forbid"}

    id: str
    name: str
    description: str
    owner: str
    technical_owner: str
    risk_tier: RiskTier
    lifecycle_stage: LifecycleStage
    system_type: SystemType
    deployed_date: date | None = None
    last_review: date | None = None
    next_review_due: date | None = None
    fda_samd_class: FDASamdClass = "not_applicable"
    fda_pccp_in_place: bool = False
    integrates_with_ehr: bool = False
    affects_clinical_decision: bool = False
    affects_patient_population: list[str] = Field(default_factory=list)
    is_generative: bool = False
    linked_artifacts: LinkedArtifacts = Field(default_factory=LinkedArtifacts)
    notes: str = ""


class Organization(BaseModel):
    """Organization-level metadata for the dashboard header and board report."""

    model_config = {"extra": "forbid"}

    name: str
    type: str
    governance_committee: str
    ai_program_lead: str
    fiscal_year_start_month: int = Field(default=7, ge=1, le=12)
