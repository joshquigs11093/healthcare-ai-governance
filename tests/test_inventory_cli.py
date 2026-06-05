"""Tests for the `hag inventory` CLI (.spec §6.1)."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from healthcare_ai_governance.cli import app

runner = CliRunner()


@pytest.fixture
def populated(write_system, inventory_dir: Path, monkeypatch, days_ago) -> Path:
    """A temp inventory with a few systems, wired up via INVENTORY_DIR."""
    write_system(id="alpha", name="Alpha", risk_tier="high", lifecycle_stage="production")
    write_system(
        id="bravo",
        name="Bravo",
        risk_tier="low",
        lifecycle_stage="production",
        next_review_due=str(days_ago(5)),
        last_review=str(days_ago(400)),
        linked_artifacts={"model_card": "artifacts/model_cards/bravo.md"},
    )
    monkeypatch.setenv("INVENTORY_DIR", str(inventory_dir))
    return inventory_dir


def test_top_level_help() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "inventory" in result.stdout


def test_version() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "healthcare-ai-governance" in result.stdout


def test_list(populated: Path) -> None:
    result = runner.invoke(app, ["inventory", "list"])
    assert result.exit_code == 0
    assert "alpha" in result.stdout
    assert "bravo" in result.stdout


def test_show_found(populated: Path) -> None:
    result = runner.invoke(app, ["inventory", "show", "alpha"])
    assert result.exit_code == 0
    assert "Alpha" in result.stdout


def test_show_missing(populated: Path) -> None:
    result = runner.invoke(app, ["inventory", "show", "nope"])
    assert result.exit_code == 1


def test_validate_ok(populated: Path) -> None:
    result = runner.invoke(app, ["inventory", "validate"])
    assert result.exit_code == 0
    assert "OK" in result.stdout


def test_validate_fails_on_bad_file(populated: Path, inventory_dir: Path) -> None:
    (inventory_dir / "systems" / "broken.yaml").write_text("id: x\n", encoding="utf-8")
    result = runner.invoke(app, ["inventory", "validate"])
    assert result.exit_code == 1


def test_overdue_exits_nonzero_when_due(populated: Path) -> None:
    result = runner.invoke(app, ["inventory", "overdue", "--as-of", "2026-06-05"])
    assert result.exit_code == 1
    assert "bravo" in result.stdout


def test_overdue_clean(write_system, inventory_dir: Path, monkeypatch) -> None:
    write_system(id="solo", lifecycle_stage="production", next_review_due="2099-01-01")
    monkeypatch.setenv("INVENTORY_DIR", str(inventory_dir))
    result = runner.invoke(app, ["inventory", "overdue", "--as-of", "2026-06-05"])
    assert result.exit_code == 0
    assert "No systems overdue" in result.stdout


def test_compliance(populated: Path) -> None:
    result = runner.invoke(app, ["inventory", "compliance"])
    assert result.exit_code == 0
    assert "stale" in result.stdout  # bravo's model card is >12 months old
    assert "missing" in result.stdout


def test_load_error_surfaces(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("INVENTORY_DIR", str(tmp_path))  # no systems/ dir
    result = runner.invoke(app, ["inventory", "list"])
    assert result.exit_code == 1
