"""`hag inventory ...` commands (.spec §6.1)."""

from __future__ import annotations

from datetime import date

import typer
from rich.console import Console
from rich.table import Table

from healthcare_ai_governance.config import get_settings
from healthcare_ai_governance.inventory.queries import (
    compliance_status,
    systems_overdue_for_review,
)
from healthcare_ai_governance.inventory.registry import load_inventory, load_system
from healthcare_ai_governance.inventory.schema import AISystem
from healthcare_ai_governance.types import InventoryValidationError

app = typer.Typer(help="Inspect and validate the AI system inventory.", no_args_is_help=True)
console = Console()
err_console = Console(stderr=True)


_TIER_STYLE = {
    "low": "green",
    "medium": "yellow",
    "high": "dark_orange",
    "critical": "bold red",
}


def _load_or_exit() -> list[AISystem]:
    settings = get_settings()
    try:
        return load_inventory(settings.inventory_dir)
    except InventoryValidationError as exc:
        err_console.print(f"[bold red]Inventory error:[/] {exc}")
        raise typer.Exit(code=1) from exc


@app.command("list")
def list_systems() -> None:
    """Tabular listing of all systems."""
    systems = _load_or_exit()
    table = Table(title="AI System Inventory")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name")
    table.add_column("Type")
    table.add_column("Risk", justify="center")
    table.add_column("Lifecycle")
    table.add_column("Owner")
    for s in systems:
        table.add_row(
            s.id,
            s.name,
            s.system_type,
            f"[{_TIER_STYLE[s.risk_tier]}]{s.risk_tier}[/]",
            s.lifecycle_stage,
            s.owner,
        )
    console.print(table)
    console.print(f"\n[dim]{len(systems)} system(s).[/]")


@app.command("show")
def show_system(system_id: str = typer.Argument(..., help="System id to display")) -> None:
    """Detail view for a single system."""
    systems = _load_or_exit()
    match = next((s for s in systems if s.id == system_id), None)
    if match is None:
        err_console.print(f"[bold red]No system with id '{system_id}'.[/]")
        raise typer.Exit(code=1)
    console.print_json(match.model_dump_json(indent=2))


@app.command("validate")
def validate() -> None:
    """Lint all inventory YAML files against the schema."""
    settings = get_settings()
    systems_dir = settings.inventory_dir / "systems"
    if not systems_dir.is_dir():
        err_console.print(f"[bold red]Not found:[/] {systems_dir}")
        raise typer.Exit(code=1)

    errors = 0
    count = 0
    for path in sorted(systems_dir.glob("*.yaml")):
        count += 1
        try:
            load_system(path)
        except InventoryValidationError as exc:
            errors += 1
            err_console.print(f"[red]FAIL[/] {exc}")
    # Re-run the full loader to catch cross-file issues (duplicate ids, etc.).
    if errors == 0:
        try:
            load_inventory(settings.inventory_dir)
        except InventoryValidationError as exc:
            errors += 1
            err_console.print(f"[red]FAIL[/] {exc}")

    if errors:
        err_console.print(f"\n[bold red]{errors} error(s) in {count} file(s).[/]")
        raise typer.Exit(code=1)
    console.print(f"[bold green]OK[/] — {count} file(s) valid.")


@app.command("overdue")
def overdue(
    as_of: str = typer.Option(None, help="Reference date (YYYY-MM-DD); defaults to today"),
) -> None:
    """List systems overdue for review."""
    systems = _load_or_exit()
    reference = date.fromisoformat(as_of) if as_of else date.today()
    due = systems_overdue_for_review(systems, reference)
    if not due:
        console.print(f"[green]No systems overdue as of {reference}.[/]")
        return
    table = Table(title=f"Overdue for review (as of {reference})")
    table.add_column("ID", style="cyan")
    table.add_column("Name")
    table.add_column("Risk", justify="center")
    table.add_column("Due")
    for s in due:
        table.add_row(
            s.id,
            s.name,
            f"[{_TIER_STYLE[s.risk_tier]}]{s.risk_tier}[/]",
            str(s.next_review_due),
        )
    console.print(table)
    raise typer.Exit(code=1)


@app.command("compliance")
def compliance() -> None:
    """Artifact-presence compliance matrix."""
    systems = _load_or_exit()
    status = compliance_status(systems)
    table = Table(title="Compliance Matrix")
    table.add_column("ID", style="cyan")
    table.add_column("Model Card", justify="center")
    table.add_column("Risk Assmt", justify="center")
    table.add_column("Fairness", justify="center")
    table.add_column("Audit", justify="center")

    def cell(present: bool, current: bool) -> str:
        if present and current:
            return "[green]current[/]"
        if present:
            return "[yellow]stale[/]"
        return "[red]missing[/]"

    for s in systems:
        st = status[s.id]
        table.add_row(
            s.id,
            cell(st["model_card_present"], st["model_card_current"]),
            cell(st["risk_assessment_present"], st["risk_assessment_current"]),
            cell(st["fairness_report_present"], st["fairness_report_current"]),
            cell(st["audit_report_present"], st["audit_report_current"]),
        )
    console.print(table)
