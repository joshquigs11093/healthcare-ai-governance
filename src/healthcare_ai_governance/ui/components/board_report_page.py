"""Board Report — executive summary page (.spec §6.6).

This page renders the on-screen board report preview. PDF export is implemented
by the board_report generator in milestone M9; until then the page surfaces the
same content it will render to PDF and notes that export is pending.
"""

from __future__ import annotations

from datetime import timedelta

import streamlit as st

from healthcare_ai_governance.dashboard_support import git_activity
from healthcare_ai_governance.inventory.queries import (
    lifecycle_distribution,
    systems_by_risk_tier,
    systems_overdue_for_review,
)
from healthcare_ai_governance.ui.context import DashboardContext


def render(ctx: DashboardContext) -> None:
    st.title("Board Report")
    default_start = ctx.today - timedelta(days=90)
    col1, col2 = st.columns(2)
    start = col1.date_input("From", value=default_start)
    end = col2.date_input("To", value=ctx.today)

    st.divider()
    st.header(f"{ctx.organization.name} — AI Governance Report")
    st.caption(f"Reporting period: {start} to {end}")

    systems = ctx.systems
    by_tier = systems_by_risk_tier(systems)
    by_stage = lifecycle_distribution(systems)
    overdue = systems_overdue_for_review(systems, ctx.today)

    st.subheader("Executive summary")
    st.markdown(
        f"""
The portfolio comprises **{len(systems)} AI systems**, of which
**{by_stage.get("production", 0)}** are in production. There are
**{len(by_tier["high"]) + len(by_tier["critical"])}** high- or critical-risk
systems and **{len(overdue)}** overdue for review.
"""
    )

    st.subheader("Portfolio statistics")
    s1, s2, s3 = st.columns(3)
    s1.metric("Total systems", len(systems))
    s2.metric("High / critical", len(by_tier["high"]) + len(by_tier["critical"]))
    s3.metric("Overdue reviews", len(overdue))

    st.subheader("Risk highlights")
    elevated = by_tier["critical"] + by_tier["high"]
    if elevated:
        for s in elevated:
            st.markdown(f"- **{s.name}** — {s.risk_tier}, {s.lifecycle_stage}")
    else:
        st.markdown("- No elevated-risk systems this period.")

    st.subheader("Overdue items")
    if overdue:
        for s in overdue:
            st.markdown(f"- **{s.name}** — was due {s.next_review_due}")
    else:
        st.markdown("- None.")

    st.subheader("Governance activity")
    activity = git_activity(ctx.repo_root, n=10, path="inventory")
    if activity:
        for e in activity:
            st.markdown(f"- {e.timestamp[:10]} — {e.subject} ({e.author})")
    else:
        st.markdown("- No version-control activity recorded.")

    st.divider()
    st.info("PDF export of this report is delivered in milestone M9 (board_report generator).")
