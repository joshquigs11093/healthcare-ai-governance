"""Recreate the Mountain Region Health demo inventory from scratch (.spec §7).

Idempotent: running it repeatedly produces byte-identical YAML. Used in CI
(``--dry-run``) to verify the demo definition still validates and that the
committed files match what the script would write.

Usage:
    python scripts/seed_demo_data.py            # write inventory/ files
    python scripts/seed_demo_data.py --dry-run  # validate only, write nothing
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

import yaml

# Allow running as a plain script (python scripts/seed_demo_data.py).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from healthcare_ai_governance.inventory.schema import (  # noqa: E402
    AISystem,
    Organization,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
INVENTORY_DIR = REPO_ROOT / "inventory"


def _organization() -> Organization:
    return Organization(
        name="Mountain Region Health",
        type="Integrated health system (fictional, for demonstration)",
        governance_committee="AI Governance & Safety Committee",
        ai_program_lead="Dr. Priya Annapareddy, Chief Health AI Officer",
        fiscal_year_start_month=7,
    )


def _systems() -> list[AISystem]:
    """The six demo systems. Dates anchored so two reviews read as overdue."""
    return [
        AISystem(
            id="sepsis-ews",
            name="Sepsis Early Warning System v2",
            description=(
                "Continuously scores inpatients for risk of sepsis using vitals, labs, "
                "and nursing assessments, surfacing alerts to the rapid response team."
            ),
            owner="Dr. Marcus Hale, Chief Medical Information Officer",
            technical_owner="Sarah Okonkwo, ML Engineering Lead",
            risk_tier="high",
            lifecycle_stage="production",
            system_type="predictive",
            deployed_date=date(2024, 8, 12),
            last_review=date(2025, 4, 15),
            next_review_due=date(2026, 4, 15),  # overdue
            integrates_with_ehr=True,
            affects_clinical_decision=True,
            affects_patient_population=["adult inpatients", "ICU", "medical-surgical units"],
            linked_artifacts={  # type: ignore[arg-type]
                "model_card": "artifacts/model_cards/sepsis-early-warning-system-v2.md",
                "risk_assessment": "artifacts/risk_assessments/sepsis-ews-2025-04.pdf",
                "monitoring_dashboard_url": "https://monitoring.example.org/sepsis-ews",
            },
            notes="Review overdue; alert-fatigue recalibration pending.",
        ),
        AISystem(
            id="readmission-risk",
            name="30-Day Readmission Risk",
            description=(
                "Predicts 30-day all-cause readmission at discharge to target "
                "care-management resources. Subject of the fairness evaluator demo."
            ),
            owner="Dr. Lena Fischer, VP Population Health",
            technical_owner="Sarah Okonkwo, ML Engineering Lead",
            risk_tier="medium",
            lifecycle_stage="production",
            system_type="predictive",
            deployed_date=date(2025, 3, 1),
            last_review=date(2026, 2, 1),
            next_review_due=date(2027, 2, 1),
            integrates_with_ehr=True,
            affects_clinical_decision=True,
            affects_patient_population=["adult inpatients at discharge"],
            linked_artifacts={  # type: ignore[arg-type]
                "model_card": "artifacts/model_cards/30-day-readmission-risk.md",
                "risk_assessment": "artifacts/risk_assessments/readmission-risk-2026-02.pdf",
                "fairness_report": "artifacts/fairness_reports/readmission-risk-2026-01.html",
            },
            notes="Logistic regression chosen for transparency.",
        ),
        AISystem(
            id="guideline-gpt",
            name="guideline-gpt RAG Assistant",
            description=(
                "Retrieval-augmented assistant that answers clinician questions by citing "
                "approved clinical guidelines. Informational only; not decision support."
            ),
            owner="Dr. Marcus Hale, Chief Medical Information Officer",
            technical_owner="Devin Park, Applied AI Engineer",
            risk_tier="medium",
            lifecycle_stage="validation",
            system_type="generative",
            last_review=date(2026, 3, 10),
            next_review_due=date(2026, 9, 10),
            integrates_with_ehr=False,
            affects_clinical_decision=False,
            affects_patient_population=["clinicians (indirect)"],
            is_generative=True,
            linked_artifacts={  # type: ignore[arg-type]
                "model_card": "artifacts/model_cards/guideline-gpt-rag-assistant.md",
                "risk_assessment": "artifacts/risk_assessments/guideline-gpt-2026-03.pdf",
                "audit_reports": ["artifacts/audit_reports/guideline-gpt-2026-03.json"],
            },
            notes="Generative — GenAI Profile questions activate in risk assessment.",
        ),
        AISystem(
            id="radiology-triage",
            name="Radiology Triage Prioritizer",
            description=(
                "Reprioritizes the radiology worklist by flagging studies with suspected "
                "acute findings for earlier read. FDA-cleared SaMD Class II with a PCCP."
            ),
            owner="Dr. Anita Rao, Chair of Radiology",
            technical_owner="Vendor-supplied (Acme Imaging AI), integration by IT",
            risk_tier="high",
            lifecycle_stage="validation",
            system_type="predictive",
            last_review=date(2026, 1, 20),
            next_review_due=date(2026, 7, 20),
            fda_samd_class="II",
            fda_pccp_in_place=True,
            integrates_with_ehr=True,
            affects_clinical_decision=True,
            affects_patient_population=["emergency department imaging", "inpatient CT"],
            linked_artifacts={  # type: ignore[arg-type]
                "model_card": "artifacts/model_cards/radiology-triage-prioritizer.md",
            },
            notes="Intentionally lacks a risk assessment to demonstrate the compliance gap.",
        ),
        AISystem(
            id="cdi-assistant",
            name="CDI Documentation Assistant",
            description=(
                "Suggests clinical documentation improvement queries by summarizing the "
                "chart. Operational, lower-risk; early in development."
            ),
            owner="Janet Liu, Director of Health Information Management",
            technical_owner="Devin Park, Applied AI Engineer",
            risk_tier="low",
            lifecycle_stage="development",
            system_type="generative",
            affects_clinical_decision=False,
            affects_patient_population=["coding and CDI staff (indirect)"],
            is_generative=True,
            notes="In development; no governance artifacts yet (expected at this stage).",
        ),
        AISystem(
            id="scheduling-optimizer",
            name="Scheduling Optimizer",
            description=(
                "Optimizes OR and clinic scheduling to reduce idle time and patient wait. "
                "Non-clinical, operational example."
            ),
            owner="Robert Chen, VP Operations",
            technical_owner="Maya Gupta, Operations Analytics",
            risk_tier="low",
            lifecycle_stage="production",
            system_type="operational",
            deployed_date=date(2024, 11, 5),
            last_review=date(2025, 2, 15),
            next_review_due=date(2026, 3, 1),  # overdue
            integrates_with_ehr=False,
            affects_clinical_decision=False,
            affects_patient_population=["surgical and clinic patients (scheduling only)"],
            linked_artifacts={  # type: ignore[arg-type]
                "risk_assessment": "artifacts/risk_assessments/scheduling-optimizer-2025-02.pdf",
            },
            notes="Review overdue; low-risk non-clinical example.",
        ),
    ]


def _dump(model: Organization | AISystem) -> str:
    payload = model.model_dump(mode="json", exclude_defaults=False)
    return yaml.safe_dump(payload, sort_keys=False, allow_unicode=True, default_flow_style=False)


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed the Mountain Region Health demo inventory.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate the demo definition without writing any files.",
    )
    args = parser.parse_args()

    org = _organization()
    systems = _systems()

    if args.dry_run:
        # model construction above already validated every record.
        print(f"[dry-run] Demo definition OK: 1 organization, {len(systems)} systems.")
        for s in systems:
            print(f"  - {s.id}: {s.risk_tier}/{s.lifecycle_stage}")
        return 0

    systems_dir = INVENTORY_DIR / "systems"
    systems_dir.mkdir(parents=True, exist_ok=True)
    (INVENTORY_DIR / "organization.yaml").write_text(_dump(org), encoding="utf-8")
    for s in systems:
        (systems_dir / f"{s.id}.yaml").write_text(_dump(s), encoding="utf-8")
    print(f"Wrote organization.yaml and {len(systems)} system file(s) to {systems_dir}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
