"""Tests for settings loading (.spec §8)."""

from __future__ import annotations

from pathlib import Path

from healthcare_ai_governance.config import get_settings


def test_defaults(monkeypatch) -> None:
    # Ensure a clean environment so defaults apply.
    for var in ("INVENTORY_DIR", "ARTIFACTS_DIR", "LLM_PROVIDER", "ANTHROPIC_MODEL"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.chdir(Path(__file__).parent)  # avoid picking up repo .env
    settings = get_settings()
    assert settings.inventory_dir == Path("./inventory")
    assert settings.llm_provider == "anthropic"
    assert settings.anthropic_model == "claude-opus-4-8"
    assert settings.pdf_classification_label == "Internal Use Only"


def test_env_override(monkeypatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("ANTHROPIC_MODEL", "claude-test")
    settings = get_settings()
    assert settings.llm_provider == "openai"
    assert settings.anthropic_model == "claude-test"
