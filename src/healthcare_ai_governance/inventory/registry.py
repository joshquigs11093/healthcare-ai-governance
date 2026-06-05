"""Load and persist inventory records (.spec §6.1).

YAML files in version control are the storage backend (ADR-002). Writes are
atomic (write-temp-then-rename) to prevent corruption on interrupted writes.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import yaml
from pydantic import ValidationError

from healthcare_ai_governance.inventory.schema import AISystem, Organization
from healthcare_ai_governance.types import InventoryValidationError


def _systems_dir(inventory_dir: Path) -> Path:
    return inventory_dir / "systems"


def _read_yaml(path: Path) -> dict[str, object]:
    try:
        with path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
    except yaml.YAMLError as exc:
        line = None
        mark = getattr(exc, "problem_mark", None)
        if mark is not None:
            line = mark.line + 1
        raise InventoryValidationError(
            f"YAML parse error: {exc}", path=str(path), line=line
        ) from exc
    if data is None:
        raise InventoryValidationError("File is empty", path=str(path))
    if not isinstance(data, dict):
        raise InventoryValidationError(
            f"Expected a mapping at the top level, got {type(data).__name__}",
            path=str(path),
        )
    return data


def _first_error_line(exc: ValidationError) -> str:
    err = exc.errors()[0]
    loc = ".".join(str(part) for part in err["loc"]) or "<root>"
    return f"{loc}: {err['msg']}"


def load_system(path: Path) -> AISystem:
    """Load and validate a single system YAML file."""
    data = _read_yaml(path)
    try:
        return AISystem.model_validate(data)
    except ValidationError as exc:
        raise InventoryValidationError(
            f"Schema validation failed: {_first_error_line(exc)}", path=str(path)
        ) from exc


def load_inventory(inventory_dir: Path) -> list[AISystem]:
    """Load all systems from ``inventory/systems/*.yaml``, sorted by id.

    Raises ``InventoryValidationError`` (with file path) on the first invalid
    file so CI fails loudly and points at the problem.
    """
    systems_dir = _systems_dir(inventory_dir)
    if not systems_dir.is_dir():
        raise InventoryValidationError(
            "Inventory systems directory not found", path=str(systems_dir)
        )

    systems: list[AISystem] = []
    seen_ids: dict[str, Path] = {}
    for path in sorted(systems_dir.glob("*.yaml")):
        system = load_system(path)
        if system.id in seen_ids:
            raise InventoryValidationError(
                f"Duplicate system id '{system.id}' (also in {seen_ids[system.id]})",
                path=str(path),
            )
        seen_ids[system.id] = path
        systems.append(system)

    systems.sort(key=lambda s: s.id)
    return systems


def load_organization(inventory_dir: Path) -> Organization:
    """Load ``inventory/organization.yaml``."""
    path = inventory_dir / "organization.yaml"
    if not path.is_file():
        raise InventoryValidationError("organization.yaml not found", path=str(path))
    data = _read_yaml(path)
    try:
        return Organization.model_validate(data)
    except ValidationError as exc:
        raise InventoryValidationError(
            f"Schema validation failed: {_first_error_line(exc)}", path=str(path)
        ) from exc


def save_system(system: AISystem, inventory_dir: Path) -> Path:
    """Atomically write a system to ``inventory/systems/{id}.yaml``.

    Writes to a temp file in the same directory, then ``os.replace`` for an
    atomic swap that never leaves a half-written file behind.
    """
    systems_dir = _systems_dir(inventory_dir)
    systems_dir.mkdir(parents=True, exist_ok=True)
    target = systems_dir / f"{system.id}.yaml"

    payload = system.model_dump(mode="json", exclude_defaults=False)
    text = yaml.safe_dump(payload, sort_keys=False, allow_unicode=True, default_flow_style=False)

    fd, tmp_name = tempfile.mkstemp(dir=systems_dir, prefix=f".{system.id}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(text)
        os.replace(tmp_name, target)
    except BaseException:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)
        raise
    return target
