"""`hag risk-assessment ...` commands (.spec §6.3)."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import typer
import yaml
from rich.console import Console

from healthcare_ai_governance.config import get_settings
from healthcare_ai_governance.inventory.registry import load_system, save_system
from healthcare_ai_governance.risk_assessment.generator import (
    build_assessment,
    generate_assessment_pdf,
)
from healthcare_ai_governance.risk_assessment.questionnaire import default_questionnaire
from healthcare_ai_governance.risk_assessment.schema import RiskAssessment
from healthcare_ai_governance.shared.pdf import PDFUnavailableError

app = typer.Typer(help="Run risk assessments from response files.", no_args_is_help=True)
console = Console()
err_console = Console(stderr=True)


@app.command("from-yaml")
def from_yaml(
    responses_path: Path = typer.Argument(..., help="YAML file with assessor info + responses"),
    system_id: str = typer.Argument(..., help="Inventory system id this assessment is for"),
    output_dir: Path = typer.Option(
        None, "--output-dir", "-o", help="Defaults to ARTIFACTS_DIR/risk_assessments"
    ),
    update_inventory: bool = typer.Option(
        False, "--update-inventory", help="Link the assessment into the inventory record"
    ),
) -> None:
    """Compute a risk assessment from a responses YAML and write a signed PDF."""
    if not responses_path.is_file():
        err_console.print(f"[bold red]Not found:[/] {responses_path}")
        raise typer.Exit(code=1)

    data = yaml.safe_load(responses_path.read_text(encoding="utf-8")) or {}
    responses = data.get("responses", {})
    if not responses:
        err_console.print("[bold red]No 'responses' found in the input file.[/]")
        raise typer.Exit(code=1)

    assessment_date = (
        date.fromisoformat(str(data["assessment_date"]))
        if data.get("assessment_date")
        else date.today()
    )
    assessment = build_assessment(
        system_id=system_id,
        assessor_name=data.get("assessor_name", "Unknown"),
        assessor_role=data.get("assessor_role", "Unknown"),
        assessment_date=assessment_date,
        responses=responses,
        questionnaire=list(default_questionnaire()),
    )

    settings = get_settings()
    out = output_dir or (settings.artifacts_dir / "risk_assessments")
    out.mkdir(parents=True, exist_ok=True)
    base = f"{system_id}-{assessment_date.isoformat()}"

    # Always write the structured assessment as a JSON sidecar.
    json_path = out / f"{base}.json"
    json_path.write_text(assessment.model_dump_json(indent=2), encoding="utf-8")

    console.print(f"Computed risk tier: [bold]{assessment.computed_risk_tier.upper()}[/]")
    console.print(f"Risk register items: {len(assessment.risk_register)}")
    console.print(f"Recommended mitigations: {len(assessment.recommended_mitigations)}")
    console.print(f"[green]wrote[/] json: {json_path}")

    pdf_path = out / f"{base}.pdf"
    try:
        generate_assessment_pdf(
            assessment, pdf_path, classification_label=settings.pdf_classification_label
        )
        console.print(f"[green]wrote[/] pdf: {pdf_path}")
    except PDFUnavailableError as exc:
        err_console.print(
            f"[yellow]PDF skipped:[/] {exc}\n(JSON written; run in Docker for the signed PDF.)"
        )

    if update_inventory:
        _link_into_inventory(system_id, pdf_path, assessment, settings.inventory_dir)
        console.print(f"[green]updated[/] inventory record for {system_id}")


def _link_into_inventory(
    system_id: str,
    pdf_path: Path,
    assessment: RiskAssessment,
    inventory_dir: Path,
) -> None:
    system_file = inventory_dir / "systems" / f"{system_id}.yaml"
    if not system_file.is_file():
        err_console.print(f"[yellow]No inventory record for {system_id}; skipping link.[/]")
        return
    system = load_system(system_file)
    system.linked_artifacts.risk_assessment = pdf_path.as_posix()
    system.last_review = assessment.assessment_date
    system.risk_tier = assessment.computed_risk_tier
    save_system(system, inventory_dir)
