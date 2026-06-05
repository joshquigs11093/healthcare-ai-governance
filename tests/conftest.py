"""Shared pytest fixtures."""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import pytest
import yaml

from healthcare_ai_governance.inventory.schema import AISystem


def _system_dict(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "id": "demo-system",
        "name": "Demo System",
        "description": "A system for tests.",
        "owner": "Owner Name",
        "technical_owner": "Tech Owner",
        "risk_tier": "medium",
        "lifecycle_stage": "production",
        "system_type": "predictive",
    }
    base.update(overrides)
    return base


@pytest.fixture
def system_factory():
    """Return a callable producing valid ``AISystem`` instances with overrides."""

    def _make(**overrides: object) -> AISystem:
        return AISystem.model_validate(_system_dict(**overrides))

    return _make


@pytest.fixture
def inventory_dir(tmp_path: Path) -> Path:
    """A temp inventory dir with an organization.yaml and a systems/ subdir."""
    (tmp_path / "systems").mkdir()
    org = {
        "name": "Test Health",
        "type": "integrated health system",
        "governance_committee": "AI Governance Committee",
        "ai_program_lead": "Dr. Lead",
    }
    (tmp_path / "organization.yaml").write_text(yaml.safe_dump(org), encoding="utf-8")
    return tmp_path


@pytest.fixture
def write_system(inventory_dir: Path):
    """Write a system dict to the temp inventory and return the inventory dir."""

    def _write(**overrides: object) -> Path:
        data = _system_dict(**overrides)
        path = inventory_dir / "systems" / f"{data['id']}.yaml"
        path.write_text(yaml.safe_dump(data), encoding="utf-8")
        return inventory_dir

    return _write


@pytest.fixture
def today() -> date:
    return date(2026, 6, 5)


@pytest.fixture
def days_ago(today: date):
    def _days_ago(n: int) -> date:
        return today - timedelta(days=n)

    return _days_ago
