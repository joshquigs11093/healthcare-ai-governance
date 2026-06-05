"""Fairness report schemas (.spec §5.4)."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field

from healthcare_ai_governance.types import DisparitySeverity


class DisparityFlag(BaseModel):
    slice_name: str
    metric: str
    disparate_groups: list[str]
    magnitude: float
    confidence_interval: tuple[float, float]
    severity: DisparitySeverity


class FairnessReport(BaseModel):
    system_id: str
    evaluation_date: date
    population_size: int
    slices_evaluated: list[str]
    metrics_by_slice: dict[str, dict[str, float]]
    disparities_flagged: list[DisparityFlag] = Field(default_factory=list)
    overall_assessment: str = ""
