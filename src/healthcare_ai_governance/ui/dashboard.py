"""Streamlit governance dashboard entry point (.spec §6.6).

Run with::

    streamlit run src/healthcare_ai_governance/ui/dashboard.py

Six pages, each reading the inventory + artifacts fresh on every rerun so updates
are never masked by caching.
"""

from __future__ import annotations

import streamlit as st

from healthcare_ai_governance.types import InventoryValidationError
from healthcare_ai_governance.ui.components import (
    board_report_page,
    compliance_matrix,
    portfolio_overview,
    reviews_due,
    risk_distribution,
    system_detail,
)
from healthcare_ai_governance.ui.context import DashboardContext

_PAGES = {
    "Portfolio Overview": portfolio_overview.render,
    "AI Systems": system_detail.render,
    "Reviews Due": reviews_due.render,
    "Risk Distribution": risk_distribution.render,
    "Compliance Matrix": compliance_matrix.render,
    "Board Report": board_report_page.render,
}


def main() -> None:
    st.set_page_config(
        page_title="Healthcare AI Governance",
        page_icon="🏥",
        layout="wide",
    )

    try:
        ctx = DashboardContext.load()
    except InventoryValidationError as exc:
        st.error(f"Could not load the inventory: {exc}")
        st.stop()
        return

    with st.sidebar:
        st.title("🏥 AI Governance")
        st.caption(ctx.organization.name)
        choice = st.radio("Page", list(_PAGES.keys()), label_visibility="collapsed")
        st.divider()
        st.caption(f"Inventory: `{ctx.settings.inventory_dir}`")

    _PAGES[choice](ctx)


if __name__ == "__main__":
    main()
