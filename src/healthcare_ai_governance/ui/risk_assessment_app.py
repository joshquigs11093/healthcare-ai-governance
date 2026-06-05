"""Interactive risk assessment workflow (.spec §6.3).

Walks the user through the questionnaire one category at a time, recomputes the
tier live, shows the accumulating risk register, and produces the signed PDF on
submission. Run with::

    streamlit run src/healthcare_ai_governance/ui/risk_assessment_app.py
"""

from __future__ import annotations

from datetime import date

import streamlit as st

from healthcare_ai_governance.config import get_settings
from healthcare_ai_governance.risk_assessment.generator import (
    build_assessment,
    generate_assessment_pdf,
)
from healthcare_ai_governance.risk_assessment.questionnaire import (
    applicable_questions,
    default_questionnaire,
    is_generative_response,
)
from healthcare_ai_governance.risk_assessment.schema import ResponseValue, RiskQuestion
from healthcare_ai_governance.risk_assessment.scoring import compute_risk_tier
from healthcare_ai_governance.shared.pdf import PDFUnavailableError, pdf_available

_CATEGORY_LABELS = {
    "use_case": "Use case",
    "data": "Data",
    "model": "Model",
    "deployment": "Deployment",
    "oversight": "Oversight",
    "ethics_equity": "Ethics & equity",
}
_TIER_COLOR = {"low": "green", "medium": "orange", "high": "red", "critical": "red"}


def _widget(q: RiskQuestion) -> ResponseValue:
    key = f"resp_{q.id}"
    if q.response_type == "yes_no":
        return st.radio(q.text, ["no", "yes"], help=q.help_text, key=key, horizontal=True)
    if q.response_type == "scale_1_5":
        return st.slider(q.text, 1, 5, 1, help=q.help_text, key=key)
    if q.response_type == "select":
        return st.selectbox(q.text, q.options, help=q.help_text, key=key)
    if q.response_type == "multiselect":
        return st.multiselect(q.text, q.options, help=q.help_text, key=key)
    return st.text_area(q.text, help=q.help_text, key=key)


def main() -> None:
    st.set_page_config(page_title="AI Risk Assessment", page_icon="📋", layout="centered")
    st.title("📋 AI Risk Assessment")
    settings = get_settings()
    questionnaire = list(default_questionnaire())

    with st.sidebar:
        st.markdown("### Assessment")
        system_id = st.text_input("System id", value="")
        assessor_name = st.text_input("Assessor name", value="")
        assessor_role = st.text_input("Assessor role", value="")

    # Collect responses category by category.
    responses: dict[str, ResponseValue] = {}
    generative = False
    for category, label in _CATEGORY_LABELS.items():
        cat_questions = [
            q
            for q in applicable_questions(questionnaire, is_generative=generative)
            if q.category == category
        ]
        if not cat_questions:
            continue
        with st.expander(label, expanded=(category == "use_case")):
            for q in cat_questions:
                responses[q.id] = _widget(q)
                st.caption(f"NIST {q.nist_rmf_subcategory}")
        # Re-evaluate generative flag after the model section so GenAI questions appear.
        generative = is_generative_response(responses)

    tier, rationale = compute_risk_tier(responses, questionnaire)
    st.markdown("### Live result")
    st.markdown(f"**Computed tier:** :{_TIER_COLOR[tier]}[{tier.upper()}]")
    with st.popover("How was this computed?"):
        for line in rationale:
            st.write(line)

    if not (system_id and assessor_name and assessor_role):
        st.info("Fill in system id, assessor name, and role in the sidebar to generate the PDF.")
        return

    if st.button("Generate signed assessment", type="primary"):
        assessment = build_assessment(
            system_id=system_id,
            assessor_name=assessor_name,
            assessor_role=assessor_role,
            assessment_date=date.today(),
            responses=responses,
            questionnaire=questionnaire,
        )
        out = settings.artifacts_dir / "risk_assessments"
        out.mkdir(parents=True, exist_ok=True)
        base = f"{system_id}-{assessment.assessment_date.isoformat()}"
        (out / f"{base}.json").write_text(assessment.model_dump_json(indent=2), encoding="utf-8")

        st.success(
            f"Assessment computed — tier {tier.upper()}, signature {assessment.signature_hash[:12]}"
        )
        if assessment.risk_register:
            st.markdown("#### Risk register")
            st.dataframe(
                [
                    {
                        "Risk": r.description,
                        "Likelihood": r.likelihood,
                        "Severity": r.severity,
                        "Score": r.inherent_risk_score,
                        "NIST": r.nist_rmf_subcategory,
                    }
                    for r in assessment.risk_register
                ],
                width="stretch",
                hide_index=True,
            )
        if assessment.recommended_mitigations:
            st.markdown("#### Recommended mitigations")
            for m in assessment.recommended_mitigations:
                st.markdown(f"- {m}")

        if pdf_available():
            pdf_path = out / f"{base}.pdf"
            try:
                generate_assessment_pdf(
                    assessment, pdf_path, classification_label=settings.pdf_classification_label
                )
                with pdf_path.open("rb") as fh:
                    st.download_button(
                        "Download signed PDF", fh.read(), file_name=pdf_path.name, type="primary"
                    )
            except PDFUnavailableError as exc:
                st.warning(f"PDF unavailable: {exc}")
        else:
            st.info("WeasyPrint not installed; JSON written. Run in Docker for the signed PDF.")


if __name__ == "__main__":
    main()
