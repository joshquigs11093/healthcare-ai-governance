"""Tests for inventory registry I/O (.spec §9)."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from healthcare_ai_governance.inventory.registry import (
    load_inventory,
    load_organization,
    load_system,
    save_system,
)
from healthcare_ai_governance.types import InventoryValidationError


def test_load_inventory_loads_and_sorts(write_system, inventory_dir: Path) -> None:
    write_system(id="zeta", name="Zeta")
    write_system(id="alpha", name="Alpha")
    systems = load_inventory(inventory_dir)
    assert [s.id for s in systems] == ["alpha", "zeta"]


def test_load_organization(inventory_dir: Path) -> None:
    org = load_organization(inventory_dir)
    assert org.name == "Test Health"
    assert org.fiscal_year_start_month == 7  # default


def test_missing_required_field_rejected(inventory_dir: Path) -> None:
    bad = {"id": "broken", "name": "No risk tier"}  # missing many required fields
    (inventory_dir / "systems" / "broken.yaml").write_text(yaml.safe_dump(bad), encoding="utf-8")
    with pytest.raises(InventoryValidationError) as exc:
        load_inventory(inventory_dir)
    assert "broken.yaml" in str(exc.value)


def test_invalid_enum_rejected(write_system, inventory_dir: Path) -> None:
    write_system(id="bad-tier", risk_tier="extreme")
    with pytest.raises(InventoryValidationError):
        load_inventory(inventory_dir)


def test_unknown_field_rejected(write_system, inventory_dir: Path) -> None:
    write_system(id="extra", surprise_field="nope")
    with pytest.raises(InventoryValidationError):
        load_inventory(inventory_dir)


def test_empty_file_rejected(inventory_dir: Path) -> None:
    (inventory_dir / "systems" / "empty.yaml").write_text("", encoding="utf-8")
    with pytest.raises(InventoryValidationError):
        load_inventory(inventory_dir)


def test_malformed_yaml_reports_line(inventory_dir: Path) -> None:
    (inventory_dir / "systems" / "bad.yaml").write_text("a: [1, 2\n  b: 3\n", encoding="utf-8")
    with pytest.raises(InventoryValidationError) as exc:
        load_inventory(inventory_dir)
    assert "bad.yaml" in str(exc.value)


def test_duplicate_id_rejected(inventory_dir: Path) -> None:
    for fname in ("one.yaml", "two.yaml"):
        data = {
            "id": "dup",
            "name": "Dup",
            "description": "d",
            "owner": "o",
            "technical_owner": "t",
            "risk_tier": "low",
            "lifecycle_stage": "production",
            "system_type": "predictive",
        }
        (inventory_dir / "systems" / fname).write_text(yaml.safe_dump(data), encoding="utf-8")
    with pytest.raises(InventoryValidationError) as exc:
        load_inventory(inventory_dir)
    assert "Duplicate" in str(exc.value)


def test_missing_systems_dir_rejected(tmp_path: Path) -> None:
    with pytest.raises(InventoryValidationError):
        load_inventory(tmp_path)


def test_save_system_roundtrip_atomic(system_factory, inventory_dir: Path) -> None:
    system = system_factory(id="roundtrip", name="Round Trip")
    path = save_system(system, inventory_dir)
    assert path.exists()
    # No leftover temp files from the atomic write.
    leftovers = list((inventory_dir / "systems").glob(".*tmp"))
    assert not leftovers
    reloaded = load_system(path)
    assert reloaded == system
