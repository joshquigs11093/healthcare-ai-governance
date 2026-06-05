"""AI Systems — browsable table with drill-down detail (.spec §6.6)."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from healthcare_ai_governance.dashboard_support import recommended_actions
from healthcare_ai_governance.inventory.schema import AISystem
from healthcare_ai_governance.ui.context import DashboardContext


def _detail(ctx: DashboardContext, system: AISystem) -> None:
    st.subheader(system.name)
    st.caption(system.description)

    actions = recommended_actions(system, ctx.today)
    if actions:
        st.warning("**Recommended actions**\n\n" + "\n".join(f"- {a}" for a in actions))
    else:
        st.success("No outstanding governance actions.")

    meta_left, meta_right = st.columns(2)
    with meta_left:
        st.markdown(
            f"""
| Field | Value |
|---|---|
| ID | `{system.id}` |
| Risk tier | **{system.risk_tier}** |
| Lifecycle | {system.lifecycle_stage} |
| Type | {system.system_type} |
| Owner | {system.owner} |
| Technical owner | {system.technical_owner} |
"""
        )
    with meta_right:
        st.markdown(
            f"""
| Field | Value |
|---|---|
| Deployed | {system.deployed_date or "—"} |
| Last review | {system.last_review or "—"} |
| Next review due | {system.next_review_due or "—"} |
| FDA SaMD class | {system.fda_samd_class} |
| PCCP in place | {"yes" if system.fda_pccp_in_place else "no"} |
| Integrates with EHR | {"yes" if system.integrates_with_ehr else "no"} |
"""
        )

    st.markdown("#### Linked artifacts")
    la = system.linked_artifacts
    artifacts = {
        "Model card": la.model_card,
        "Risk assessment": la.risk_assessment,
        "Fairness report": la.fairness_report,
    }
    for label, rel in artifacts.items():
        if rel is None:
            st.markdown(f"- {label}: _none_")
            continue
        path = ctx.repo_root / rel
        exists = path.exists()
        marker = "" if exists else "  ⚠️ _(file not generated yet)_"
        st.markdown(f"- {label}: `{rel}`{marker}")
        if exists and Path(rel).suffix == ".pdf":
            with path.open("rb") as fh:
                st.download_button(
                    f"Download {label}",
                    fh.read(),
                    file_name=path.name,
                    key=f"dl-{system.id}-{label}",
                )
    if la.audit_reports:
        st.markdown("- Audit reports:")
        for rel in la.audit_reports:
            st.markdown(f"    - `{rel}`")

    if system.notes:
        st.markdown("#### Notes")
        st.info(system.notes)


def render(ctx: DashboardContext) -> None:
    st.title("AI Systems")
    systems = ctx.systems

    with st.sidebar:
        st.markdown("### Filters")
        tiers = st.multiselect("Risk tier", sorted({s.risk_tier for s in systems}))
        stages = st.multiselect("Lifecycle", sorted({s.lifecycle_stage for s in systems}))
        types = st.multiselect("Type", sorted({s.system_type for s in systems}))
        ehr_only = st.checkbox("Integrates with EHR only")

    filtered = [
        s
        for s in systems
        if (not tiers or s.risk_tier in tiers)
        and (not stages or s.lifecycle_stage in stages)
        and (not types or s.system_type in types)
        and (not ehr_only or s.integrates_with_ehr)
    ]

    st.dataframe(
        [
            {
                "ID": s.id,
                "Name": s.name,
                "Type": s.system_type,
                "Risk": s.risk_tier,
                "Lifecycle": s.lifecycle_stage,
                "Owner": s.owner,
                "Next review": str(s.next_review_due) if s.next_review_due else "—",
            }
            for s in filtered
        ],
        width="stretch",
        hide_index=True,
    )
    st.caption(f"{len(filtered)} of {len(systems)} system(s).")

    if not filtered:
        return
    st.divider()
    options = {f"{s.name} ({s.id})": s for s in filtered}
    selected = st.selectbox("View detail for:", list(options.keys()))
    _detail(ctx, options[selected])
