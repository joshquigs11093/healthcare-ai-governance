# Mapping: FDA AI/ML (SaMD) Guidance → Toolkit

This document maps the FDA's guidance for AI/ML-enabled medical device software to
the components of this toolkit. It is relevant only for systems that **are**
FDA-regulated devices; many healthcare AI systems are not. The inventory tracks
device status (`fda_samd_class`, `fda_pccp_in_place`) so the portfolio shows which
systems fall under FDA jurisdiction.

> **Scope note.** FDA premarket review, quality-system requirements, and
> postmarket obligations are the manufacturer's responsibility and go well beyond
> what any documentation toolkit provides. This mapping shows where the toolkit's
> artifacts *support* the relevant principles for a deploying organization — not
> that using the toolkit satisfies FDA requirements. Reviewed against the source
> documents annually.

## Relevant FDA documents

- **Good Machine Learning Practice (GMLP) Guiding Principles** — 10 principles
  (FDA / Health Canada / MHRA, October 2021).
- **Predetermined Change Control Plan (PCCP)** guidance for AI-enabled device
  software functions — final, December 2024.
- **Transparency for Machine Learning-Enabled Medical Devices: Guiding
  Principles** — June 2024.
- **Total Product Lifecycle (TPLC)** for AI-enabled devices — draft, January 2025.

## GMLP guiding principles → toolkit support

| GMLP principle (theme) | Toolkit support | Coverage |
|---|---|---|
| 1. Multidisciplinary expertise across the lifecycle | Governance committee roles (primer); intake | Out of scope (org) |
| 3. Clinical study participants/data represent the intended population | Model card `development_dataset_demographics`; fairness representativeness | Partial |
| 4. Training and test sets are independent | Documented in model card `evaluation_method` | Partial (records, not enforces) |
| 5. Reference datasets are well characterized | Model card `development_dataset_description` | Partial |
| 6. Model design suited to data & intended use | Model card; risk `model.*` | Partial |
| 7. Human–AI team performance considered | Risk `deployment.human_oversight`; model card `clinical_workflow_integration` | Partial |
| 8. Testing under clinically relevant conditions | Model card `external_validation_process` | Partial |
| 9. Clear, essential information to users | **Model card** (HTI-1-aligned disclosures) | Direct |
| 10. Deployed models monitored for performance | Risk `deployment.monitoring`; inventory review cadence | Partial |

## PCCP (Predetermined Change Control Plan)

A PCCP lets a manufacturer pre-specify how a model may change post-clearance
without a new submission. For a deploying organization, the governance question is
whether a device has a PCCP and how updates are communicated.

| PCCP concern | Toolkit support |
|---|---|
| Is a PCCP in place for this device? | Inventory `fda_pccp_in_place` (boolean, shown on dashboard) |
| Vendor change/update process | Vendor model card request (Q18); procurement checklist |
| Risk of unreviewed model updates | Risk `model.third_party`; mitigation `vendor_transparency` |
| Re-review after an update | Inventory review cadence; "reviews due" dashboard page |

## Transparency principles (June 2024)

The model card directly supports the transparency principles by disclosing
intended use, logic/inputs/outputs, development data, performance (including by
subgroup), and limitations — see `docs/mappings/onc-hti1-mapping.md` for the
field-level breakdown, which substantially overlaps.

## Risk class tracking

The inventory records FDA SaMD risk class (`fda_samd_class`: I–IV or
`not_applicable`). The dashboard's Risk Distribution page includes a "Risk by FDA
SaMD class" view so the committee can see regulated systems at a glance. Over
1,350 AI-enabled devices had FDA authorization by early 2026; tracking which
inventory systems are devices is increasingly part of routine governance.

## What this mapping does not claim

The toolkit does not perform FDA submissions, establish a quality management
system, conduct clinical validation, or make a device compliant. It helps a
*deploying* organization document and track the governance-relevant facts about
devices it uses.

---

*Sources: FDA GMLP Guiding Principles (Oct 2021); FDA PCCP guidance (final, Dec
2024); FDA Transparency for ML-Enabled Medical Devices (Jun 2024); FDA TPLC draft
(Jan 2025). Verify against the primary FDA documents.*
