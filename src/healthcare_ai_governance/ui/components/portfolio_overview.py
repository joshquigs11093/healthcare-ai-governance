"""Portfolio Overview — dashboard landing page (.spec §6.6)."""

from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from healthcare_ai_governance.dashboard_support import git_activity
from healthcare_ai_governance.inventory.queries import (
    lifecycle_distribution,
    systems_by_risk_tier,
    systems_overdue_for_review,
)
from healthcare_ai_governance.types import RISK_TIERS
from healthcare_ai_governance.ui.context import DashboardContext

_TIER_COLORS = {
    "low": "#2e7d32",
    "medium": "#f9a825",
    "high": "#ef6c00",
    "critical": "#c62828",
}


def render(ctx: DashboardContext) -> None:
    st.title(ctx.organization.name)
    st.caption(f"{ctx.organization.type} — as of {ctx.today}")

    systems = ctx.systems
    by_tier = systems_by_risk_tier(systems)
    by_stage = lifecycle_distribution(systems)
    overdue = systems_overdue_for_review(systems, ctx.today)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Systems", len(systems))
    c2.metric("In production", by_stage.get("production", 0))
    c3.metric("High / critical", len(by_tier["high"]) + len(by_tier["critical"]))
    c4.metric("Overdue reviews", len(overdue))

    if overdue:
        names = ", ".join(s.name for s in overdue)
        st.warning(f"**{len(overdue)} system(s) overdue for review:** {names}")

    left, right = st.columns(2)
    with left:
        st.subheader("Risk tier distribution")
        tier_counts = [len(by_tier[t]) for t in RISK_TIERS]
        donut = go.Figure(
            go.Pie(
                labels=list(RISK_TIERS),
                values=tier_counts,
                hole=0.55,
                marker={"colors": [_TIER_COLORS[t] for t in RISK_TIERS]},
            )
        )
        donut.update_layout(margin={"t": 10, "b": 10, "l": 10, "r": 10}, height=320)
        st.plotly_chart(donut, width="stretch")
    with right:
        st.subheader("Lifecycle distribution")
        stages = list(by_stage.keys())
        bar = go.Figure(go.Bar(x=stages, y=[by_stage[s] for s in stages]))
        bar.update_layout(margin={"t": 10, "b": 10, "l": 10, "r": 10}, height=320)
        st.plotly_chart(bar, width="stretch")

    st.subheader("Recent governance activity")
    activity = git_activity(ctx.repo_root, n=10, path="inventory")
    if not activity:
        st.info("No version-control history available for the inventory directory.")
    else:
        st.dataframe(
            [{"When": e.timestamp, "Who": e.author, "Change": e.subject} for e in activity],
            width="stretch",
            hide_index=True,
        )
