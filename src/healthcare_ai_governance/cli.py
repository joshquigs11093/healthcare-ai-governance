"""Top-level ``hag`` command-line entry point.

Sub-apps are mounted per capability as they are built (.spec §6). Capabilities
with heavy optional dependencies (model-card PDF, audit, fairness) are imported
lazily so that ``hag --help`` and the inventory commands work even when those
extras are not installed.
"""

from __future__ import annotations

import typer

from healthcare_ai_governance import __version__
from healthcare_ai_governance.inventory.cli import app as inventory_app
from healthcare_ai_governance.model_card.cli import app as model_card_app

app = typer.Typer(
    help="healthcare-ai-governance (hag) — governance tooling for healthcare AI programs.",
    no_args_is_help=True,
    add_completion=False,
)

app.add_typer(inventory_app, name="inventory")
app.add_typer(model_card_app, name="model-card")


@app.command()
def version() -> None:
    """Print the toolkit version."""
    typer.echo(f"healthcare-ai-governance {__version__}")


if __name__ == "__main__":
    app()
