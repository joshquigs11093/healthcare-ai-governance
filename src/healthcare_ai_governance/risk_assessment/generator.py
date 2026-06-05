"""Assemble and render risk assessments, including the signed PDF (.spec §6.3)."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import jinja2

from healthcare_ai_governance.risk_assessment.mitigations import (
    MitigationRule,
    recommend_mitigations,
)
from healthcare_ai_governance.risk_assessment.questionnaire import (
    applicable_questions,
    is_generative_response,
)
from healthcare_ai_governance.risk_assessment.schema import (
    ResponseValue,
    RiskAssessment,
    RiskItem,
    RiskQuestion,
)
from healthcare_ai_governance.risk_assessment.scoring import (
    _max_response_score,
    _score_response,
    compute_risk_tier,
)
from healthcare_ai_governance.shared.pdf import html_to_pdf
from healthcare_ai_governance.shared.signing import content_hash
from healthcare_ai_governance.types import Likelihood, Severity

_LIKELIHOOD: tuple[Likelihood, ...] = (
    "rare",
    "unlikely",
    "possible",
    "likely",
    "almost_certain",
)
_SEVERITY: tuple[Severity, ...] = (
    "negligible",
    "minor",
    "moderate",
    "major",
    "catastrophic",
)

# A question contributes a risk-register entry when its normalized score is at
# or above this fraction of its maximum.
_REGISTER_THRESHOLD = 0.5

_TEMPLATE_DIR = Path(__file__).parent / "templates"
_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(str(_TEMPLATE_DIR)),
    autoescape=jinja2.select_autoescape(enabled_extensions=("html.j2",), default_for_string=False),
    trim_blocks=True,
    lstrip_blocks=True,
    keep_trailing_newline=True,
)


def _selected_response_text(question: RiskQuestion, response: ResponseValue) -> str:
    if isinstance(response, list):
        return ", ".join(str(r) for r in response)
    return str(response)


def build_risk_register(
    responses: dict[str, ResponseValue], questions: list[RiskQuestion]
) -> list[RiskItem]:
    """Derive a deterministic risk register from elevated responses.

    For each answered, applicable question whose normalized score meets the
    threshold, emit a RiskItem. Likelihood scales with the normalized score;
    severity scales with the question's weight (its governance importance).
    """
    register: list[RiskItem] = []
    for q in questions:
        response = responses.get(q.id)
        if response is None:
            continue
        max_score = _max_response_score(q)
        if max_score == 0:
            continue
        normalized = _score_response(q, response) / max_score
        if normalized < _REGISTER_THRESHOLD:
            continue
        likelihood_idx = min(4, round(normalized * 4))
        severity_idx = q.weight - 1
        register.append(
            RiskItem(
                description=f"{q.text} (response: {_selected_response_text(q, response)})",
                likelihood=_LIKELIHOOD[likelihood_idx],
                severity=_SEVERITY[severity_idx],
                inherent_risk_score=(likelihood_idx + 1) * (severity_idx + 1),
                recommended_mitigations=[],
                nist_rmf_subcategory=q.nist_rmf_subcategory,
            )
        )
    register.sort(key=lambda r: r.inherent_risk_score, reverse=True)
    return register


def build_assessment(
    *,
    system_id: str,
    assessor_name: str,
    assessor_role: str,
    assessment_date: date,
    responses: dict[str, ResponseValue],
    questionnaire: list[RiskQuestion],
    rules: list[MitigationRule] | None = None,
) -> RiskAssessment:
    """Compute the tier, risk register, mitigations, and signature for an assessment."""
    tier, _rationale = compute_risk_tier(responses, questionnaire)
    is_generative = is_generative_response(responses)
    questions = applicable_questions(questionnaire, is_generative=is_generative)
    register = build_risk_register(responses, questions)
    mitigations = recommend_mitigations(responses, tier, rules)

    assessment = RiskAssessment(
        system_id=system_id,
        assessor_name=assessor_name,
        assessor_role=assessor_role,
        assessment_date=assessment_date,
        responses=responses,
        computed_risk_tier=tier,
        is_generative=is_generative,
        risk_register=register,
        recommended_mitigations=mitigations,
        signature_hash="",
    )
    assessment.signature_hash = _assessment_signature(assessment)
    return assessment


def _assessment_signature(assessment: RiskAssessment) -> str:
    """SHA-256 over the assessment content, excluding the signature field itself."""
    payload = assessment.model_dump(mode="json")
    payload.pop("signature_hash", None)
    return content_hash(payload)


def render_assessment_html(
    assessment: RiskAssessment,
    classification_label: str,
    generation_date: date,
) -> str:
    template = _env.get_template("assessment.html.j2")
    return template.render(
        a=assessment,
        classification=classification_label,
        generation_date=generation_date.isoformat(),
        short_hash=assessment.signature_hash[:12],
        full_hash=assessment.signature_hash,
    )


def generate_assessment_pdf(
    assessment: RiskAssessment,
    output_path: Path,
    classification_label: str = "Internal Use Only",
    generation_date: date | None = None,
) -> Path:
    """Render the assessment to a signed PDF (.spec §6.3).

    The "signature" is the content hash embedded in the footer; it detects
    tampering between generation and any later modification. It does not
    authenticate the assessor (see shared/signing.py).
    """
    html = render_assessment_html(assessment, classification_label, generation_date or date.today())
    return html_to_pdf(html, output_path)
