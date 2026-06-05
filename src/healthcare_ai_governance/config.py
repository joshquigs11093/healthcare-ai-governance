"""Runtime configuration loaded from environment variables (.spec §8)."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Toolkit configuration. All values overridable via environment variables.

    See .spec §8 for the canonical table. Defaults are chosen so the inventory
    and dashboard work out-of-the-box against the committed demo data.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    inventory_dir: Path = Field(default=Path("./inventory"))
    artifacts_dir: Path = Field(default=Path("./artifacts"))

    llm_provider: Literal["anthropic", "openai"] = Field(default="anthropic")
    anthropic_api_key: str | None = Field(default=None)
    # Bumped from the spec's claude-opus-4-7 to the current latest (4.8).
    anthropic_model: str = Field(default="claude-opus-4-8")
    openai_api_key: str | None = Field(default=None)
    openai_model: str = Field(default="gpt-4o")

    pdf_classification_label: str = Field(default="Internal Use Only")
    log_level: str = Field(default="INFO")


def get_settings() -> Settings:
    """Return a freshly-loaded ``Settings`` instance.

    Not cached: tests and the dashboard expect environment changes to take
    effect on the next call.
    """
    return Settings()
