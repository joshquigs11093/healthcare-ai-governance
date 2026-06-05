"""Tests for the `hag model-card` CLI (.spec §6.2)."""

from __future__ import annotations

from pathlib import Path

import yaml
from typer.testing import CliRunner

from healthcare_ai_governance.cli import app

runner = CliRunner()


def _write_card_yaml(card, path: Path) -> Path:
    path.write_text(yaml.safe_dump(card.model_dump(mode="json"), sort_keys=False), encoding="utf-8")
    return path


def test_validate_ok(sample_model_card, tmp_path: Path) -> None:
    yaml_path = _write_card_yaml(sample_model_card, tmp_path / "card.yaml")
    result = runner.invoke(app, ["model-card", "validate", str(yaml_path)])
    assert result.exit_code == 0
    assert "OK" in result.stdout


def test_validate_missing_file() -> None:
    result = runner.invoke(app, ["model-card", "validate", "does-not-exist.yaml"])
    assert result.exit_code == 1


def test_validate_invalid_schema(tmp_path: Path) -> None:
    bad = tmp_path / "bad.yaml"
    bad.write_text("model_name: only this field\n", encoding="utf-8")
    result = runner.invoke(app, ["model-card", "validate", str(bad)])
    assert result.exit_code == 1


def test_render_markdown_html(sample_model_card, tmp_path: Path) -> None:
    yaml_path = _write_card_yaml(sample_model_card, tmp_path / "card.yaml")
    out = tmp_path / "out"
    result = runner.invoke(
        app,
        ["model-card", "render", str(yaml_path), "-o", str(out), "-f", "markdown", "-f", "html"],
    )
    assert result.exit_code == 0
    assert (out / "30-day-readmission-risk-v1.2.md").exists()
    assert (out / "30-day-readmission-risk-v1.2.html").exists()


def test_new_scaffold(tmp_path: Path) -> None:
    out = tmp_path / "new_card.yaml"
    result = runner.invoke(
        app,
        ["model-card", "new", str(out), "--model-name", "Test Model", "--version", "0.1"],
    )
    assert result.exit_code == 0
    assert out.exists()
    data = yaml.safe_load(out.read_text(encoding="utf-8"))
    assert data["model_name"] == "Test Model"
    assert data["version"] == "0.1"
    # The scaffold must contain every schema field so it round-trips after editing.
    from healthcare_ai_governance.model_card.schema import ModelCard

    assert set(data.keys()) == set(ModelCard.model_fields.keys())


def test_new_refuses_overwrite(tmp_path: Path) -> None:
    out = tmp_path / "exists.yaml"
    out.write_text("x\n", encoding="utf-8")
    result = runner.invoke(
        app, ["model-card", "new", str(out), "--model-name", "M", "--version", "1"]
    )
    assert result.exit_code == 1
