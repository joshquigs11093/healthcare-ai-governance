"""Compliance Matrix — artifact-presence grid with CSV export (.spec §6.6)."""

from __future__ import annotations

import csv
import io

import streamlit as st

from healthcare_ai_governance.dashboard_support import compliance_rows
from healthcare_ai_governance.ui.context import DashboardContext

_BADGE = {
    "current": "🟢 current",
    "stale": "🟡 stale",
    "missing": "🔴 missing",
}


def render(ctx: DashboardContext) -> None:
    st.title("Compliance Matrix")
    st.caption(
        "Green = present and reviewed within 12 months · Yellow = present but stale "
        "(>12 months) · Red = missing."
    )

    rows = compliance_rows(ctx.systems, as_of=ctx.today)
    display = [{k: (_BADGE.get(v, v)) for k, v in row.items()} for row in rows]
    st.dataframe(display, width="stretch", hide_index=True)

    # CSV export uses the raw labels (not the emoji badges).
    buffer = io.StringIO()
    if rows:
        writer = csv.DictWriter(buffer, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    st.download_button(
        "Export to CSV",
        buffer.getvalue(),
        file_name="compliance_matrix.csv",
        mime="text/csv",
    )
