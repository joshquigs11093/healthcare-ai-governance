"""`hag audit ...` commands (.spec §6.5)."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import typer
from rich.console import Console

from healthcare_ai_governance.config import get_settings
from healthcare_ai_governance.output_auditor.auditor import OutputAuditor
from healthcare_ai_governance.output_auditor.reporter import summarize
from healthcare_ai_governance.output_auditor.schema import LLMOutput
from healthcare_ai_governance.types import FINDING_SEVERITY_ORDER, FindingSeverity, GovernanceError

app = typer.Typer(
    help="Audit LLM outputs for PHI, claims, jailbreaks, and citations.", no_args_is_help=True
)
console = Console()
err_console = Console(stderr=True)


def _load_outputs(path: Path) -> list[LLMOutput]:
    if not path.is_file():
        err_console.print(f"[bold red]Not found:[/] {path}")
        raise typer.Exit(code=1)
    outputs: list[LLMOutput] = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            outputs.append(LLMOutput.model_validate(json.loads(line)))
        except (json.JSONDecodeError, ValueError) as exc:
            err_console.print(f"[bold red]Invalid output on line {i}:[/] {exc}")
            raise typer.Exit(code=1) from exc
    return outputs


def _build_auditor(config_path: Path, system_id: str | None) -> OutputAuditor:
    try:
        auditor = OutputAuditor.from_config_file(config_path)
    except GovernanceError as exc:
        err_console.print(f"[bold red]{exc}[/]")
        raise typer.Exit(code=1) from exc
    if system_id:
        auditor._config.system_id = system_id  # noqa: SLF001 - CLI override of config
    return auditor


@app.command()
def run(
    outputs_path: Path = typer.Argument(..., help="JSONL file of outputs to audit"),
    config: Path = typer.Option(..., "--config", help="Audit config YAML"),
    system: str = typer.Option(None, "--system", help="System id (overrides config)"),
    output_dir: Path = typer.Option(None, "--output-dir", "-o"),
) -> None:
    """Audit a batch of outputs and write a JSON report."""
    auditor = _build_auditor(config, system)
    outputs = _load_outputs(outputs_path)
    report = auditor.audit(outputs)

    settings = get_settings()
    out = output_dir or (settings.artifacts_dir / "audit_reports")
    out.mkdir(parents=True, exist_ok=True)
    report_path = out / f"{report.system_id}-{date.today().isoformat()}.json"
    report_path.write_text(report.model_dump_json(indent=2), encoding="utf-8")

    console.print(summarize(report))
    console.print(f"[green]wrote[/] {report_path}")


@app.command()
def ci(
    outputs_path: Path = typer.Argument(..., help="JSONL file of outputs to audit"),
    config: Path = typer.Option(..., "--config", help="Audit config YAML"),
    system: str = typer.Option(None, "--system", help="System id (overrides config)"),
    fail_on: FindingSeverity = typer.Option(
        "critical", "--fail-on", help="Exit non-zero if findings at/above this severity exist"
    ),
) -> None:
    """Audit in CI mode: exit non-zero when findings reach the fail-on severity."""
    auditor = _build_auditor(config, system)
    outputs = _load_outputs(outputs_path)
    report = auditor.audit(outputs)
    console.print(summarize(report))

    threshold = FINDING_SEVERITY_ORDER[fail_on]
    breached = [
        f
        for check_findings in report.findings.values()
        for f in check_findings
        if FINDING_SEVERITY_ORDER[f.severity] >= threshold
    ]
    if breached:
        err_console.print(f"[bold red]{len(breached)} finding(s) at or above '{fail_on}'.[/]")
        raise typer.Exit(code=1)
    console.print(f"[bold green]PASS[/] — no findings at or above '{fail_on}'.")
