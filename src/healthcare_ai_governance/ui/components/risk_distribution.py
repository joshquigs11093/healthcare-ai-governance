"""Risk Distribution — portfolio risk analysis (.spec §6.6)."""

from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from healthcare_ai_governance.dashboard_support import risk_lifecycle_matrix
from healthcare_ai_governance.types import RISK_TIER_ORDER
from healthcare_ai_governance.ui.context import DashboardContext


def render(ctx: DashboardContext) -> None:
    st.title("Risk Distribution")
    systems = ctx.systems

    rows, cols, matrix = risk_lifecycle_matrix(systems)
    st.subheader("Lifecycle stage × risk tier")
    heatmap = go.Figure(
        go.Heatmap(
            z=matrix,
            x=cols,
            y=rows,
            text=matrix,
            texttemplate="%{text}",
            colorscale="OrRd",
            showscale=False,
        )
    )
    heatmap.update_layout(margin={"t": 10, "b": 10, "l": 10, "r": 10}, height=360)
    st.plotly_chart(heatmap, width="stretch")

    st.subheader("Critical and high-risk systems")
    elevated = sorted(
        (s for s in systems if s.risk_tier in {"high", "critical"}),
        key=lambda s: RISK_TIER_ORDER[s.risk_tier],
        reverse=True,
    )
    if not elevated:
        st.success("No high or critical systems.")
    else:
        st.dataframe(
            [
                {
                    "ID": s.id,
                    "Name": s.name,
                    "Risk": s.risk_tier,
                    "Lifecycle": s.lifecycle_stage,
                    "Clinical": "yes" if s.affects_clinical_decision else "no",
                }
                for s in elevated
            ],
            width="stretch",
            hide_index=True,
        )

    fda_systems = [s for s in systems if s.fda_samd_class != "not_applicable"]
    if fda_systems:
        st.subheader("Risk by FDA SaMD class")
        class_counts: dict[str, int] = {}
        for s in fda_systems:
            class_counts[s.fda_samd_class] = class_counts.get(s.fda_samd_class, 0) + 1
        classes = sorted(class_counts.keys())
        bar = go.Figure(go.Bar(x=classes, y=[class_counts[c] for c in classes]))
        bar.update_layout(margin={"t": 10, "b": 10, "l": 10, "r": 10}, height=280)
        st.plotly_chart(bar, width="stretch")
