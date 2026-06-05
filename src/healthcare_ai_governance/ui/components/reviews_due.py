"""Reviews Due — upcoming and overdue review calendar (.spec §6.6)."""

from __future__ import annotations

from datetime import timedelta

import streamlit as st

from healthcare_ai_governance.inventory.queries import systems_overdue_for_review
from healthcare_ai_governance.ui.context import DashboardContext


def render(ctx: DashboardContext) -> None:
    st.title("Reviews Due")

    lookahead = st.slider("Lookahead window (days)", min_value=30, max_value=365, value=90, step=30)
    horizon = ctx.today + timedelta(days=lookahead)

    overdue = systems_overdue_for_review(ctx.systems, ctx.today)
    if overdue:
        st.error(f"**{len(overdue)} overdue**")
        st.dataframe(
            [
                {"ID": s.id, "Name": s.name, "Risk": s.risk_tier, "Was due": str(s.next_review_due)}
                for s in sorted(overdue, key=lambda s: s.next_review_due or ctx.today)
            ],
            width="stretch",
            hide_index=True,
        )
    else:
        st.success("Nothing overdue.")

    upcoming = [
        s
        for s in ctx.systems
        if s.next_review_due is not None and ctx.today <= s.next_review_due <= horizon
    ]
    st.subheader(f"Upcoming in the next {lookahead} days")
    if not upcoming:
        st.info("No reviews scheduled in this window.")
        return
    st.dataframe(
        [
            {
                "ID": s.id,
                "Name": s.name,
                "Risk": s.risk_tier,
                "Due": str(s.next_review_due),
                "In days": (s.next_review_due - ctx.today).days if s.next_review_due else None,
            }
            for s in sorted(upcoming, key=lambda s: s.next_review_due or horizon)
        ],
        width="stretch",
        hide_index=True,
    )
