"""Build and render the executive board report (.spec §6.6 Board Report)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import jinja2

from healthcare_ai_governance.dashboard_support import ActivityEntry, git_activity
from healthcare_ai_governance.inventory.queries import (
    compliance_status,
    lifecycle_distribution,
    systems_by_risk_tier,
    systems_overdue_for_review,
)
from healthcare_ai_governance.inventory.schema import AISystem, Organization
from healthcare_ai_governance.shared.pdf import html_to_pdf
from healthcare_ai_governance.types import RISK_TIER_ORDER, LifecycleStage, RiskTier

_TEMPLATE_DIR = Path(__file__).parent / "templates"
_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(str(_TEMPLATE_DIR)),
    autoescape=jinja2.select_autoescape(enabled_extensions=("html.j2",)),
    trim_blocks=True,
    lstrip_blocks=True,
)


@dataclass
class BoardReportData:
    """Everything the board report renders. Pure data — assembled deterministically."""

    organization: str
    period_start: date
    period_end: date
    generation_date: date
    total_systems: int
    production_count: int
    high_critical_count: int
    overdue_count: int
    by_tier: dict[RiskTier, int]
    by_lifecycle: dict[LifecycleStage, int]
    elevated_systems: list[AISystem]
    overdue_systems: list[AISystem]
    recommendations: list[str]
    activity: list[ActivityEntry] = field(default_factory=list)

    @property
    def executive_summary(self) -> str:
        return (
            f"The portfolio comprises {self.total_systems} AI system(s), "
            f"{self.production_count} in production. "
            f"{self.high_critical_count} are high- or critical-risk and "
            f"{self.overdue_count} are overdue for review."
        )


def _recommendations(
    systems: list[AISystem], overdue: list[AISystem], as_of: date
) -> list[str]:
    """Deterministic, prioritized recommendations from the portfolio state."""
    recs: list[str] = []
    if overdue:
        recs.append(
            f"Schedule and complete reviews for {len(overdue)} overdue system(s): "
            + ", ".join(s.name for s in overdue)
            + "."
        )
    status = compliance_status(systems, as_of=as_of)
    elevated_missing_ra = [
        s
        for s in systems
        if s.risk_tier in {"high", "critical"}
        and s.lifecycle_stage in {"production", "validation"}
        and not status[s.id]["risk_assessment_present"]
    ]
    if elevated_missing_ra:
        recs.append(
            "Complete risk assessments for high/critical systems lacking one: "
            + ", ".join(s.name for s in elevated_missing_ra)
            + "."
        )
    clinical_missing_card = [
        s
        for s in systems
        if s.affects_clinical_decision
        and s.lifecycle_stage == "production"
        and not status[s.id]["model_card_present"]
    ]
    if clinical_missing_card:
        recs.append(
            "Produce model cards for production clinical systems lacking one: "
            + ", ".join(s.name for s in clinical_missing_card)
            + "."
        )
    fda_no_pccp = [
        s for s in systems if s.fda_samd_class != "not_applicable" and not s.fda_pccp_in_place
    ]
    if fda_no_pccp:
        recs.append(
            "Confirm change-control (PCCP) status with vendors for FDA-regulated "
            "systems without one: " + ", ".join(s.name for s in fda_no_pccp) + "."
        )
    if not recs:
        recs.append("No outstanding portfolio-level actions; maintain the review cadence.")
    return recs


def build_board_report_data(
    systems: list[AISystem],
    organization: Organization,
    *,
    period_start: date,
    period_end: date,
    generation_date: date,
    repo_root: Path | None = None,
) -> BoardReportData:
    """Assemble the board report from an inventory snapshot (.spec §6.6)."""
    by_tier_lists = systems_by_risk_tier(systems)
    by_tier = {tier: len(items) for tier, items in by_tier_lists.items()}
    by_lifecycle = lifecycle_distribution(systems)
    overdue = systems_overdue_for_review(systems, period_end)
    elevated = sorted(
        by_tier_lists["critical"] + by_tier_lists["high"],
        key=lambda s: RISK_TIER_ORDER[s.risk_tier],
        reverse=True,
    )
    activity = git_activity(repo_root, n=10, path="inventory") if repo_root else []

    return BoardReportData(
        organization=organization.name,
        period_start=period_start,
        period_end=period_end,
        generation_date=generation_date,
        total_systems=len(systems),
        production_count=by_lifecycle.get("production", 0),
        high_critical_count=by_tier["high"] + by_tier["critical"],
        overdue_count=len(overdue),
        by_tier=by_tier,
        by_lifecycle=by_lifecycle,
        elevated_systems=elevated,
        overdue_systems=overdue,
        recommendations=_recommendations(systems, overdue, period_end),
        activity=activity,
    )


def render_board_report_html(data: BoardReportData, classification_label: str) -> str:
    template = _env.get_template("board_report.html.j2")
    return template.render(d=data, classification=classification_label)


def generate_board_report_pdf(
    data: BoardReportData,
    output_path: Path,
    classification_label: str = "Internal Use Only",
) -> Path:
    """Render the board report to a PDF (.spec §6.6)."""
    html = render_board_report_html(data, classification_label)
    return html_to_pdf(html, output_path)
