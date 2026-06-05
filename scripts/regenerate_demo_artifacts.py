"""Regenerate demo artifacts from code (.spec §4 scripts, §6.2).

Currently renders model cards for the demo systems that have one. Extended in
later milestones to also (re)produce risk assessments, fairness reports, and
audit reports. Outputs land in ``artifacts/`` (which is gitignored).

Usage:
    python scripts/regenerate_demo_artifacts.py
    python scripts/regenerate_demo_artifacts.py --formats markdown html
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from healthcare_ai_governance.model_card.generator import (  # noqa: E402
    generate_model_card,
)
from healthcare_ai_governance.model_card.schema import ModelCard  # noqa: E402
from healthcare_ai_governance.output_auditor.auditor import OutputAuditor  # noqa: E402
from healthcare_ai_governance.output_auditor.schema import LLMOutput  # noqa: E402
from healthcare_ai_governance.shared.pdf import pdf_available  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
MODEL_CARDS_DIR = REPO_ROOT / "artifacts" / "model_cards"
AUDIT_DIR = REPO_ROOT / "artifacts" / "audit_reports"
DATA_DIR = REPO_ROOT / "data"


def _readmission_card() -> ModelCard:
    return ModelCard(
        model_name="30-Day Readmission Risk",
        version="1.2",
        model_type="Logistic regression",
        developer="Mountain Region Health — ML Engineering",
        contact="ml-governance@example.org",
        last_updated=date(2026, 1, 15),
        primary_use_cases=["Flag discharges at elevated 30-day readmission risk"],
        primary_users=["Care management nurses", "Discharge planners"],
        out_of_scope_uses=["Denying care", "Insurance underwriting"],
        intended_care_setting=["Inpatient discharge"],
        target_patient_population="Adult inpatients at discharge",
        clinical_workflow_integration="Score surfaced in the discharge planning worklist",
        clinical_decision_supported="Prioritization of care-management outreach",
        fda_regulatory_status="Not a medical device",
        hipaa_data_classification="PHI (limited data set for development)",
        details_and_output="Penalized logistic regression; outputs a 0-1 risk score.",
        purpose="Target finite care-management resources to the highest-risk patients.",
        cautioned_out_of_scope_use="Not validated for pediatric or obstetric populations.",
        inputs_used=["Age", "Prior admissions", "Comorbidity flags", "Primary insurance"],
        output_used="Calibrated probability of 30-day all-cause readmission",
        quantitative_measures_of_performance={"auroc": 0.726, "auprc": 0.341},
        development_dataset_description="5,000 synthetic patients generated with Synthea.",
        development_dataset_demographics={"age": "18-89", "sex": "51% F / 49% M"},
        external_validation_process="Held-out temporal split; recalibrated quarterly.",
        performance_metrics={"auroc": 0.726, "brier": 0.118},
        performance_by_subgroup={
            "race:Black": {"auroc": 0.701},
            "race:White": {"auroc": 0.733},
        },
        evaluation_method="5-fold cross-validation with bootstrap confidence intervals.",
        known_limitations=["Synthetic training data; not validated on real patients."],
        fairness_considerations="AUROC gap across race slices monitored; see fairness report.",
        safety_considerations="Advisory only; never auto-actions care.",
        monitoring_plan="Monthly calibration drift check; quarterly fairness re-evaluation.",
        retirement_criteria="Retire if calibration drift exceeds threshold for two cycles.",
        incident_contacts="ml-governance@example.org; on-call pager 555-0100",
    )


_DEMO_CARDS = {"readmission-risk": _readmission_card}


def main() -> int:
    parser = argparse.ArgumentParser(description="Regenerate demo artifacts.")
    parser.add_argument(
        "--formats",
        nargs="+",
        default=["markdown", "html"] + (["pdf"] if pdf_available() else []),
        help="Formats to render (markdown html pdf).",
    )
    args = parser.parse_args()

    if "pdf" in args.formats and not pdf_available():
        print("WeasyPrint unavailable; skipping PDF. (Run in Docker for PDF output.)")
        args.formats = [f for f in args.formats if f != "pdf"]

    for system_id, builder in _DEMO_CARDS.items():
        written = generate_model_card(builder(), MODEL_CARDS_DIR, args.formats)
        for fmt, path in written.items():
            print(f"[{system_id}] {fmt}: {path.relative_to(REPO_ROOT)}")

    _generate_demo_audit()
    return 0


def _generate_demo_audit() -> None:
    """Run the output auditor on the sample outputs (all five checks active)."""
    config_path = DATA_DIR / "audit_config.yaml"
    outputs_path = DATA_DIR / "sample_audit_outputs.jsonl"
    if not (config_path.is_file() and outputs_path.is_file()):
        return
    auditor = OutputAuditor.from_config_file(config_path)
    outputs = [
        LLMOutput.model_validate_json(line)
        for line in outputs_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    report = auditor.audit(outputs)
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    out = AUDIT_DIR / "guideline-gpt-2026-03.json"
    out.write_text(report.model_dump_json(indent=2), encoding="utf-8")
    n_findings = sum(len(v) for v in report.findings.values())
    print(f"[guideline-gpt] audit: {out.relative_to(REPO_ROOT)} ({n_findings} findings)")


if __name__ == "__main__":
    raise SystemExit(main())
