"""Headless render test for every dashboard page (.spec §6.6, M3 acceptance).

Uses Streamlit's AppTest to execute each page against the committed demo
inventory and asserts no exception is raised. Skipped if Streamlit is not
installed or the demo inventory is absent.
"""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest  # noqa: E402

_REPO_ROOT = Path(__file__).resolve().parent.parent
_SCRIPT = _REPO_ROOT / "src" / "healthcare_ai_governance" / "ui" / "dashboard.py"
_PAGES = [
    "Portfolio Overview",
    "AI Systems",
    "Reviews Due",
    "Risk Distribution",
    "Compliance Matrix",
    "Board Report",
]

pytestmark = pytest.mark.skipif(
    not (_REPO_ROOT / "inventory" / "systems").is_dir(),
    reason="demo inventory not present",
)


@pytest.fixture(autouse=True)
def _point_at_demo(monkeypatch) -> None:
    monkeypatch.setenv("INVENTORY_DIR", str(_REPO_ROOT / "inventory"))
    monkeypatch.chdir(_REPO_ROOT)


@pytest.mark.parametrize("page", _PAGES)
def test_page_renders(page: str) -> None:
    at = AppTest.from_file(str(_SCRIPT), default_timeout=60).run()
    assert not at.exception
    at.radio[0].set_value(page).run()
    assert not at.exception, f"{page} raised: {at.exception}"
