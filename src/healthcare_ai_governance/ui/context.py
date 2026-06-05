"""Shared dashboard context object passed to every page (.spec §6.6).

The inventory and organization are reloaded on every Streamlit rerun (no caching
that would mask updates), so a context is cheap to construct per page load.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

from healthcare_ai_governance.config import Settings, get_settings
from healthcare_ai_governance.inventory.registry import load_inventory, load_organization
from healthcare_ai_governance.inventory.schema import AISystem, Organization


@dataclass
class DashboardContext:
    settings: Settings
    organization: Organization
    systems: list[AISystem]
    repo_root: Path
    today: date

    @classmethod
    def load(cls) -> DashboardContext:
        settings = get_settings()
        return cls(
            settings=settings,
            organization=load_organization(settings.inventory_dir),
            systems=load_inventory(settings.inventory_dir),
            repo_root=Path.cwd(),
            today=date.today(),
        )
