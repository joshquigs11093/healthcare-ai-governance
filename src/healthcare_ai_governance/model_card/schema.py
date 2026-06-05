"""Model card schema (.spec §5.2).

Based on Mitchell et al. (2019) with healthcare extensions and alignment to the
HTI-1 source attribute set. Sections are present even if the regulation's
certification requirement is removed, because the underlying transparency value
is independent of certification (.spec §1.3, §5.2).
"""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field


class ModelCard(BaseModel):
    model_config = {"extra": "forbid"}

    # Identity
    model_name: str
    version: str
    model_type: str
    developer: str
    contact: str
    last_updated: date

    # Intended use (Mitchell et al.)
    primary_use_cases: list[str]
    primary_users: list[str]
    out_of_scope_uses: list[str]

    # Healthcare extensions
    intended_care_setting: list[str]
    target_patient_population: str
    clinical_workflow_integration: str
    clinical_decision_supported: str
    fda_regulatory_status: str
    hipaa_data_classification: str

    # HTI-1 source attribute alignment
    details_and_output: str  # Algorithm description, output description
    purpose: str  # Specific clinical purpose
    cautioned_out_of_scope_use: str  # Aligned with HTI-1 (b)(11)(iv)(C)
    inputs_used: list[str]  # Data inputs (HTI-1 source attribute)
    output_used: str  # Algorithm output (HTI-1 source attribute)
    quantitative_measures_of_performance: dict[str, float]
    development_dataset_description: str
    development_dataset_demographics: dict[str, str]
    external_validation_process: str

    # Performance and fairness
    performance_metrics: dict[str, float]
    performance_by_subgroup: dict[str, dict[str, float]]
    evaluation_method: str

    # Ethical and operational
    known_limitations: list[str]
    fairness_considerations: str
    safety_considerations: str
    monitoring_plan: str
    retirement_criteria: str
    incident_contacts: str = Field(
        description="Who to contact and how, when the model misbehaves in production."
    )
