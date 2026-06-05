"""`hag model-card ...` commands (.spec §6.2)."""

from __future__ import annotations

from pathlib import Path

import typer
import yaml
from pydantic import ValidationError
from rich.console import Console

from healthcare_ai_governance.config import get_settings
from healthcare_ai_governance.model_card.generator import (
    SUPPORTED_FORMATS,
    generate_model_card,
)
from healthcare_ai_governance.model_card.schema import ModelCard
from healthcare_ai_governance.shared.pdf import PDFUnavailableError

app = typer.Typer(help="Create and render model cards.", no_args_is_help=True)
console = Console()
err_console = Console(stderr=True)


def _load_card(yaml_path: Path) -> ModelCard:
    if not yaml_path.is_file():
        err_console.print(f"[bold red]Not found:[/] {yaml_path}")
        raise typer.Exit(code=1)
    data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    try:
        return ModelCard.model_validate(data)
    except ValidationError as exc:
        err = exc.errors()[0]
        loc = ".".join(str(p) for p in err["loc"]) or "<root>"
        err_console.print(f"[bold red]Invalid model card:[/] {loc}: {err['msg']}")
        raise typer.Exit(code=1) from exc


@app.command()
def render(
    yaml_path: Path = typer.Argument(..., help="Path to a model card YAML file"),
    output_dir: Path = typer.Option(
        None, "--output-dir", "-o", help="Output directory (defaults to ARTIFACTS_DIR/model_cards)"
    ),
    formats: list[str] = typer.Option(
        ["markdown", "html", "pdf"],
        "--format",
        "-f",
        help=f"Formats to render. Choices: {', '.join(SUPPORTED_FORMATS)}",
    ),
) -> None:
    """Render a model card YAML to the requested formats."""
    card = _load_card(yaml_path)
    settings = get_settings()
    out = output_dir or (settings.artifacts_dir / "model_cards")
    try:
        written = generate_model_card(
            card,
            out,
            formats,
            classification_label=settings.pdf_classification_label,
        )
    except PDFUnavailableError as exc:
        err_console.print(f"[bold red]PDF unavailable:[/] {exc}")
        raise typer.Exit(code=2) from exc
    for fmt, path in written.items():
        console.print(f"[green]wrote[/] {fmt}: {path}")


@app.command()
def validate(yaml_path: Path = typer.Argument(..., help="Path to a model card YAML file")) -> None:
    """Validate a model card YAML against the schema."""
    _load_card(yaml_path)
    console.print(f"[bold green]OK[/] — {yaml_path} is a valid model card.")


@app.command()
def new(
    output: Path = typer.Argument(..., help="Path to write the new model card YAML"),
    model_name: str = typer.Option(..., prompt="Model name"),
    version: str = typer.Option(..., prompt="Version"),
) -> None:
    """Scaffold a new model card YAML with placeholders to fill in."""
    if output.exists():
        err_console.print(f"[bold red]Refusing to overwrite:[/] {output}")
        raise typer.Exit(code=1)
    skeleton = _skeleton(model_name, version)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        yaml.safe_dump(skeleton, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )
    console.print(f"[green]Created[/] {output} — fill in the placeholder fields, then `render`.")


def _skeleton(model_name: str, version: str) -> dict[str, object]:
    """A fully-populated placeholder model card (all schema fields present)."""
    return {
        "model_name": model_name,
        "version": version,
        "model_type": "TODO (e.g. logistic regression, transformer)",
        "developer": "TODO",
        "contact": "TODO",
        "last_updated": "2026-01-01",
        "primary_use_cases": ["TODO"],
        "primary_users": ["TODO"],
        "out_of_scope_uses": ["TODO"],
        "intended_care_setting": ["TODO"],
        "target_patient_population": "TODO",
        "clinical_workflow_integration": "TODO",
        "clinical_decision_supported": "TODO",
        "fda_regulatory_status": "Not a medical device / TODO",
        "hipaa_data_classification": "TODO",
        "details_and_output": "TODO",
        "purpose": "TODO",
        "cautioned_out_of_scope_use": "TODO",
        "inputs_used": ["TODO"],
        "output_used": "TODO",
        "quantitative_measures_of_performance": {"auroc": 0.0},
        "development_dataset_description": "TODO",
        "development_dataset_demographics": {"age": "TODO"},
        "external_validation_process": "TODO",
        "performance_metrics": {"auroc": 0.0},
        "performance_by_subgroup": {"example_group": {"auroc": 0.0}},
        "evaluation_method": "TODO",
        "known_limitations": ["TODO"],
        "fairness_considerations": "TODO",
        "safety_considerations": "TODO",
        "monitoring_plan": "TODO",
        "retirement_criteria": "TODO",
        "incident_contacts": "TODO",
    }
