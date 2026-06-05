# Mapping: ONC HTI-1 Source Attributes → Model Card Fields

This document maps the **source attribute** categories established by the ONC
**HTI-1 Final Rule** (89 Fed. Reg. 1192, published January 9, 2024; effective
February 8, 2024; compliance date January 1, 2026) to the fields of this
toolkit's model card schema (`src/healthcare_ai_governance/model_card/schema.py`).

> **Regulatory status note.** HTI-1 introduced algorithmic transparency
> requirements for predictive Decision Support Interventions (DSIs) in certified
> health IT, including a defined set of "source attributes" a certified system
> must make available. ASTP/ONC subsequently proposed **HTI-5 (late 2025)**, a
> deregulation rule that would *remove* certification requirements for CDS
> algorithms, including this disclosure requirement. **The outcome is uncertain.**
> This toolkit treats the source-attribute content as a useful transparency
> baseline regardless of certification status, because the underlying disclosures
> are independently valuable for governance. Reviewed against the source documents
> annually.

## Source attribute categories → model card fields

HTI-1 organizes the required disclosures into categories often summarized as the
"source attributes." The table maps each to the model card field(s) that carry it.

| HTI-1 source attribute (theme) | Model card field(s) |
|---|---|
| Details — name, developer, version, contact | `model_name`, `version`, `developer`, `contact`, `last_updated` |
| Purpose — intended use of the intervention | `purpose`, `primary_use_cases`, `clinical_decision_supported` |
| Intended patient population / care setting | `target_patient_population`, `intended_care_setting` |
| Cautioned / out-of-scope uses [ref. (b)(11)(iv)(C)] | `cautioned_out_of_scope_use`, `out_of_scope_uses` |
| Inputs used (variables / data elements) | `inputs_used`, `details_and_output` |
| Output produced and how it is used | `output_used`, `details_and_output` |
| Development data — description | `development_dataset_description` |
| Development data — demographics / representativeness | `development_dataset_demographics` |
| Validation / evaluation process (incl. external) | `external_validation_process`, `evaluation_method` |
| Quantitative performance measures | `quantitative_measures_of_performance`, `performance_metrics` |
| Fairness / subgroup performance | `performance_by_subgroup`, `fairness_considerations` |
| Ongoing maintenance / update / monitoring | `monitoring_plan`, `retirement_criteria` |
| Use of the intervention safely (limitations) | `known_limitations`, `safety_considerations` |

## Healthcare extensions beyond HTI-1

The model card schema includes fields that go beyond the HTI-1 minimum because
they are useful for healthcare governance:

| Field | Purpose |
|---|---|
| `fda_regulatory_status` | Track whether the system is an FDA-regulated device |
| `hipaa_data_classification` | Record the data sensitivity (de-identified / LDS / PHI) |
| `clinical_workflow_integration` | How the output reaches the point of care |
| `incident_contacts` | Who to contact when the model misbehaves |

## Ordering

The Markdown model card template (`model_card.md.j2`) is laid out in the HTI-1
source-attribute order (Details → Purpose → Intended use → Inputs/Outputs →
Development data → Validation/performance → Fairness → Limitations/operations) so
that a card produced by this toolkit can serve as HTI-1 conformance evidence *if*
the certification requirement is reinstated, or as voluntary transparency if it is
not.

## What this mapping does not claim

Producing a model card with these fields does not, by itself, make a system
HTI-1-certified or compliant; certification involves the certified-health-IT
process and ONC criteria beyond document content. This mapping aligns *content*,
not certification status.

---

*Sources: ONC HTI-1 Final Rule, 89 Fed. Reg. 1192 (Jan 9, 2024); ASTP/ONC HTI-5
Proposed Rule (Dec 2025). Verify attribute definitions against the primary rule
text.*
