"""Tests for the `hag risk-assessment` CLI (.spec §6.3)."""

from __future__ import annotations

import json
from pathlib import Path

import yaml
from typer.testing import CliRunner

from healthcare_ai_governance.cli import app
from healthcare_ai_governance.inventory.registry import load_system

runner = CliRunner()


def _responses_file(path: Path, **overrides: object) -> Path:
    data = {
        "assessor_name": "Dr. Test",
        "assessor_role": "CMIO",
        "assessment_date": "2026-06-01",
        "responses": {
            "use_case.autonomy": "yes",
            "model.validation": "not yet validated",
            "deployment.human_oversight": "no human oversight",
        },
    }
    data.update(overrides)
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    return path


def test_from_yaml_writes_json_and_reports_tier(tmp_path: Path) -> None:
    responses = _responses_file(tmp_path / "responses.yaml")
    out = tmp_path / "out"
    result = runner.invoke(
        app, ["risk-assessment", "from-yaml", str(responses), "sepsis-ews", "-o", str(out)]
    )
    assert result.exit_code == 0
    assert "CRITICAL" in result.stdout  # autonomy=yes forces critical
    json_path = out / "sepsis-ews-2026-06-01.json"
    assert json_path.exists()
    data = json.loads(json_path.read_text(encoding="utf-8"))
    assert data["computed_risk_tier"] == "critical"
    assert data["signature_hash"]
    assert data["recommended_mitigations"]


def test_from_yaml_missing_file() -> None:
    result = runner.invoke(app, ["risk-assessment", "from-yaml", "nope.yaml", "sys"])
    assert result.exit_code == 1


def test_from_yaml_no_responses(tmp_path: Path) -> None:
    bad = tmp_path / "bad.yaml"
    bad.write_text("assessor_name: x\n", encoding="utf-8")
    result = runner.invoke(app, ["risk-assessment", "from-yaml", str(bad), "sys"])
    assert result.exit_code == 1


def test_from_yaml_updates_inventory(tmp_path: Path, monkeypatch, write_system) -> None:
    inv = write_system(id="sepsis-ews", risk_tier="low", lifecycle_stage="production")
    monkeypatch.setenv("INVENTORY_DIR", str(inv))
    responses = _responses_file(tmp_path / "responses.yaml")
    out = tmp_path / "out"
    result = runner.invoke(
        app,
        [
            "risk-assessment",
            "from-yaml",
            str(responses),
            "sepsis-ews",
            "-o",
            str(out),
            "--update-inventory",
        ],
    )
    assert result.exit_code == 0
    updated = load_system(inv / "systems" / "sepsis-ews.yaml")
    assert updated.risk_tier == "critical"
    assert updated.linked_artifacts.risk_assessment is not None
    assert updated.last_review is not None
