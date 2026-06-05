"""Smoke test: the Streamlit UI modules import without error.

The dashboard itself is integration-tested manually (and excluded from the
coverage gate), but a broken import should fail CI loudly. Skipped if Streamlit
is not installed (it is an optional ``dashboard`` extra).
"""

from __future__ import annotations

import importlib

import pytest

pytest.importorskip("streamlit")

_MODULES = [
    "healthcare_ai_governance.ui.context",
    "healthcare_ai_governance.ui.dashboard",
    "healthcare_ai_governance.ui.risk_assessment_app",
    "healthcare_ai_governance.ui.components.portfolio_overview",
    "healthcare_ai_governance.ui.components.system_detail",
    "healthcare_ai_governance.ui.components.reviews_due",
    "healthcare_ai_governance.ui.components.risk_distribution",
    "healthcare_ai_governance.ui.components.compliance_matrix",
    "healthcare_ai_governance.ui.components.board_report_page",
]


@pytest.mark.parametrize("module", _MODULES)
def test_ui_module_imports(module: str) -> None:
    mod = importlib.import_module(module)
    assert mod is not None


def test_dashboard_pages_wired() -> None:
    from healthcare_ai_governance.ui.dashboard import _PAGES

    assert set(_PAGES) == {
        "Portfolio Overview",
        "AI Systems",
        "Reviews Due",
        "Risk Distribution",
        "Compliance Matrix",
        "Board Report",
    }
    assert all(callable(fn) for fn in _PAGES.values())
