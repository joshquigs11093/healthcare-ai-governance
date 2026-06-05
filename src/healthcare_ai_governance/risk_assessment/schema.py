"""Risk assessment schemas (.spec §5.3, §6.3)."""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

from healthcare_ai_governance.types import Likelihood, RiskTier, Severity

ResponseType = Literal["select", "multiselect", "yes_no", "scale_1_5", "text"]
QuestionCategory = Literal["use_case", "data", "model", "deployment", "oversight", "ethics_equity"]

# Value type for a single questionnaire response.
ResponseValue = str | list[str] | int


class RiskQuestion(BaseModel):
    """One questionnaire item (.spec §6.3).

    ``generative_only`` extends the spec model to support the documented
    behavior that Generative AI Profile questions activate only when the system
    is generative.
    """

    model_config = {"extra": "forbid"}

    id: str
    category: QuestionCategory
    nist_rmf_subcategory: str
    text: str
    help_text: str
    response_type: ResponseType
    options: list[str] = Field(default_factory=list)
    weight: int = Field(default=1, ge=1, le=5)
    tier_overrides: dict[str, RiskTier] = Field(default_factory=dict)
    generative_only: bool = False


class RiskItem(BaseModel):
    """A single entry in the risk register (.spec §5.3)."""

    description: str
    likelihood: Likelihood
    severity: Severity
    inherent_risk_score: int = Field(ge=1, le=25)
    recommended_mitigations: list[str]
    nist_rmf_subcategory: str


class RiskAssessment(BaseModel):
    """A completed risk assessment (.spec §5.3)."""

    system_id: str
    assessor_name: str
    assessor_role: str
    assessment_date: date
    responses: dict[str, ResponseValue]
    computed_risk_tier: RiskTier
    is_generative: bool
    risk_register: list[RiskItem]
    recommended_mitigations: list[str]
    signature_hash: str = ""  # SHA-256 of canonical content, filled at finalization
