"""Board Report — executive PDF generation page (.spec §6.6)."""

from __future__ import annotations

from datetime import datetime, timedelta

import streamlit as st

from healthcare_ai_governance.board_report.generator import (
    build_board_report_data,
    generate_board_report_pdf,
)
from healthcare_ai_governance.shared.pdf import PDFUnavailableError, pdf_available
from healthcare_ai_governance.ui.context import DashboardContext


def render(ctx: DashboardContext) -> None:
    st.title("Board Report")
    default_start = ctx.today - timedelta(days=90)
    col1, col2 = st.columns(2)
    start = col1.date_input("From", value=default_start)
    end = col2.date_input("To", value=ctx.today)

    data = build_board_report_data(
        ctx.systems,
        ctx.organization,
        period_start=start,
        period_end=end,
        generation_date=ctx.today,
        repo_root=ctx.repo_root,
    )

    st.divider()
    st.header(f"{ctx.organization.name} — AI Governance Report")
    st.caption(f"Reporting period: {start} to {end}")

    st.subheader("Executive summary")
    st.markdown(data.executive_summary)

    st.subheader("Portfolio statistics")
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Total systems", data.total_systems)
    s2.metric("In production", data.production_count)
    s3.metric("High / critical", data.high_critical_count)
    s4.metric("Overdue reviews", data.overdue_count)

    st.subheader("Risk highlights")
    if data.elevated_systems:
        for s in data.elevated_systems:
            st.markdown(f"- **{s.name}** — {s.risk_tier}, {s.lifecycle_stage}")
    else:
        st.markdown("- No elevated-risk systems this period.")

    st.subheader("Overdue items")
    if data.overdue_systems:
        for s in data.overdue_systems:
            st.markdown(f"- **{s.name}** — was due {s.next_review_due}")
    else:
        st.markdown("- None.")

    st.subheader("Recommendations")
    for r in data.recommendations:
        st.markdown(f"- {r}")

    st.divider()
    if not pdf_available():
        st.info("WeasyPrint not installed; PDF export is available in the Docker image.")
        return

    if st.button("Generate board report PDF", type="primary"):
        out_dir = ctx.settings.artifacts_dir / "board_reports"
        out_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")  # noqa: DTZ005 - local stamp
        pdf_path = out_dir / f"board-report-{stamp}.pdf"
        try:
            generate_board_report_pdf(
                data, pdf_path, classification_label=ctx.settings.pdf_classification_label
            )
        except PDFUnavailableError as exc:
            st.error(f"PDF unavailable: {exc}")
            return
        with pdf_path.open("rb") as fh:
            st.download_button(
                "Download board report PDF",
                fh.read(),
                file_name=pdf_path.name,
                mime="application/pdf",
                type="primary",
            )
