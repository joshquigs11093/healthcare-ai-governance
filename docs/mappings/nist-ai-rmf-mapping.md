# Mapping: NIST AI Risk Management Framework → Toolkit

This document maps the **NIST AI Risk Management Framework (AI RMF 1.0,
January 2023)** and its **Generative AI Profile (NIST AI 600-1, July 2024)** to
the components of this toolkit, and states plainly which subcategories are **out
of scope** (because they are organizational/cultural and cannot be satisfied by a
tool).

> **Scope and honesty note.** The AI RMF is a voluntary framework. The full Core
> defines four functions with many categories and subcategories; the Generative
> AI Profile adds generative-specific suggested actions. This is a
> *representative* mapping of the subcategories most relevant to the artifacts
> this toolkit produces — not a claim of complete coverage. A tool can produce
> evidence and structure; it cannot, by itself, establish the accountability and
> culture the GOVERN function requires. Reviewed against the source documents
> annually.

## How to read this

- **Subcategory** uses NIST's notation (e.g. `MEASURE 2.11`).
- **Toolkit support** names the component(s) that produce relevant evidence.
- **Coverage** is one of: **Direct** (the tool produces the artifact),
  **Partial** (the tool supports but does not complete it), **Out of scope**
  (organizational; the tool only records the outcome).

## GOVERN — culture, accountability, policy

| Subcategory (theme) | Toolkit support | Coverage |
|---|---|---|
| GOVERN 1.1 — legal/regulatory requirements understood | Risk assessment (`oversight.governance_approval`); mappings docs | Partial |
| GOVERN 1.2 — trustworthy-AI characteristics integrated | Risk assessment categories; model card | Partial |
| GOVERN 1.5 — ongoing monitoring & periodic review | Inventory review cadence + dashboard "reviews due" | Direct |
| GOVERN 2.1 — roles and responsibilities | Inventory `owner` / `technical_owner`; intake template | Partial |
| GOVERN 4.x — culture, safety mindset, documentation | Templates and primer | Out of scope (cultural) |
| GOVERN 6.1 — third-party/supply-chain risk | Vendor model card request; procurement checklist; risk `model.third_party` | Partial |

## MAP — context and risk framing

| Subcategory (theme) | Toolkit support | Coverage |
|---|---|---|
| MAP 1.1 — intended purpose / context established | Model card (purpose, intended use); risk `use_case.*` | Direct |
| MAP 1.6 — affected individuals / equity impact | Inventory `affects_patient_population`; risk `ethics_equity.equity_impact` | Partial |
| MAP 4.1 — PHI / privacy risk identified | Risk `data.phi`; output auditor PHI leakage check | Direct |
| MAP 5.1 — impacts characterized (reversibility) | Risk `use_case.reversibility` | Partial |

## MEASURE — analysis and tracking

| Subcategory (theme) | Toolkit support | Coverage |
|---|---|---|
| MEASURE 2.3 — performance/accuracy evaluated | Model card metrics; fairness report | Direct |
| MEASURE 2.5 — validation under conditions of use | Model card (external validation); risk `model.validation` | Partial |
| MEASURE 2.9 — model explainability/interpretability | Risk `model.explainability`; model card | Partial |
| MEASURE 2.11 — fairness/bias evaluated by subgroup | **Fairness evaluator** (demographic parity, equalized odds, etc.) | Direct |
| MEASURE 2.12 — environmental/ongoing monitoring | Risk `deployment.monitoring`; inventory review | Partial |

## MANAGE — acting on risk

| Subcategory (theme) | Toolkit support | Coverage |
|---|---|---|
| MANAGE 1.3 — human oversight of high-risk decisions | Risk `use_case.autonomy`, `deployment.human_oversight` (tier-override floors) | Direct |
| MANAGE 2.x — mitigation planning | Risk assessment mitigations (`data/mitigations.yaml`) | Direct |
| MANAGE 4.1 — monitoring & rollback | Risk `deployment.rollback`; incident-response template | Partial |
| MANAGE 4.3 — incident response | `templates/ai-incident-response.md`; risk `oversight.incident_response` | Partial |

## Generative AI Profile (NIST AI 600-1)

The toolkit activates additional questions when a system is generative and adds
output-level checks:

| GenAI risk area | Toolkit support |
|---|---|
| Confabulation / unsupported output (MEASURE 2.3 GAI) | Risk `gen.hallucination`; output auditor `unsupported_claims` |
| Data privacy / PHI leakage (MAP 4.1 GAI) | Risk `gen.phi_leakage`; output auditor `phi_leakage` |
| Information integrity / grounding (MEASURE 2.9 GAI) | Risk `gen.grounding`; output auditor `citation_validity` |
| Misuse / prompt injection (MANAGE 2.2 GAI) | Risk `gen.misuse`; output auditor `jailbreak` |
| Content provenance (GOVERN 1.2 GAI) | Risk `gen.content_provenance` |

## Explicitly out of scope

The toolkit does **not** establish organizational culture (GOVERN 4.x), make
risk-acceptance decisions, perform the clinical validation it documents, or
guarantee regulatory compliance. It produces evidence and structure to support
human decisions mapped to these subcategories.

---

*Sources: NIST AI RMF 1.0 (Jan 2023), <https://www.nist.gov/itl/ai-risk-management-framework>;
NIST AI 600-1 Generative AI Profile (Jul 2024). Verify subcategory text against
the primary documents.*
