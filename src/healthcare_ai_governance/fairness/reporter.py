"""Build and render fairness reports (.spec §6.4)."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import numpy as np
import numpy.typing as npt
import pandas as pd

from healthcare_ai_governance.fairness.metrics import (
    MetricResult,
    compute_metrics,
    severity_for,
)
from healthcare_ai_governance.fairness.schema import DisparityFlag, FairnessReport
from healthcare_ai_governance.fairness.slicer import SlicerConfig, build_slices
from healthcare_ai_governance.types import DisparitySeverity

# Metrics for which a max-min spread implies a disparity worth flagging.
_DISPARITY_METRICS = ("demographic_parity", "equal_opportunity", "equalized_odds", "ppv_parity")


def build_report(
    *,
    system_id: str,
    y_true: npt.ArrayLike,
    y_pred: npt.ArrayLike,
    y_score: npt.ArrayLike,
    df: pd.DataFrame,
    evaluation_date: date,
    config: SlicerConfig | None = None,
    n_boot: int = 200,
    seed: int = 12345,
) -> FairnessReport:
    """Evaluate fairness across all configured slices. Pure (no rendering)."""
    yt = np.asarray(y_true, dtype=np.int_)
    yp = np.asarray(y_pred, dtype=np.int_)
    ys = np.asarray(y_score, dtype=np.float64)
    slices = build_slices(df, config)

    metrics_by_slice: dict[str, dict[str, float]] = {}
    flags: list[DisparityFlag] = []

    for slice_name, sensitive in slices.items():
        results = compute_metrics(yt, yp, ys, sensitive, n_boot=n_boot, seed=seed)
        metrics_by_slice[slice_name] = {
            name: round(res.magnitude, 4) for name, res in results.items()
        }
        for metric_name in _DISPARITY_METRICS:
            res = results[metric_name]
            severity = severity_for(res.magnitude)
            if severity != "informational":
                flags.append(
                    DisparityFlag(
                        slice_name=slice_name,
                        metric=metric_name,
                        disparate_groups=res.disparate_groups,
                        magnitude=round(res.magnitude, 4),
                        confidence_interval=(
                            round(res.confidence_interval[0], 4),
                            round(res.confidence_interval[1], 4),
                        ),
                        severity=severity,
                    )
                )

    flags.sort(key=lambda f: f.magnitude, reverse=True)
    report = FairnessReport(
        system_id=system_id,
        evaluation_date=evaluation_date,
        population_size=int(len(yt)),
        slices_evaluated=list(slices.keys()),
        metrics_by_slice=metrics_by_slice,
        disparities_flagged=flags,
        overall_assessment=_assess(flags),
    )
    return report


def _assess(flags: list[DisparityFlag]) -> str:
    critical = [f for f in flags if f.severity == "critical"]
    warning = [f for f in flags if f.severity == "warning"]
    if critical:
        return (
            f"{len(critical)} critical and {len(warning)} warning-level disparities found. "
            "Remediation is recommended before deployment or continued use."
        )
    if warning:
        return (
            f"{len(warning)} warning-level disparities found. Review and monitor; "
            "consider mitigation."
        )
    return "No material disparities detected above the warning threshold."


def roc_curve(y_true: npt.ArrayLike, y_score: npt.ArrayLike) -> tuple[list[float], list[float]]:
    """Return (fpr, tpr) points for a binary ROC curve (numpy implementation)."""
    yt = np.asarray(y_true, dtype=np.int_)
    ys = np.asarray(y_score, dtype=np.float64)
    order = np.argsort(-ys)
    yt = yt[order]
    p = int(np.sum(yt == 1))
    n = int(np.sum(yt == 0))
    if p == 0 or n == 0:
        return [0.0, 1.0], [0.0, 1.0]
    tps = np.cumsum(yt == 1)
    fps = np.cumsum(yt == 0)
    tpr = [0.0, *(tps / p).tolist()]
    fpr = [0.0, *(fps / n).tolist()]
    return fpr, tpr


def reliability_curve(
    y_true: npt.ArrayLike, y_score: npt.ArrayLike, bins: int = 10
) -> tuple[list[float], list[float]]:
    """Return (mean_predicted, observed_frequency) per probability bin."""
    yt = np.asarray(y_true, dtype=np.float64)
    ys = np.asarray(y_score, dtype=np.float64)
    edges = np.linspace(0.0, 1.0, bins + 1)
    mean_pred: list[float] = []
    obs_freq: list[float] = []
    for i in range(bins):
        lo, hi = edges[i], edges[i + 1]
        m = (ys >= lo) & (ys < hi) if i < bins - 1 else (ys >= lo) & (ys <= hi)
        if np.any(m):
            mean_pred.append(float(np.mean(ys[m])))
            obs_freq.append(float(np.mean(yt[m])))
    return mean_pred, obs_freq


_SEVERITY_BADGE: dict[DisparitySeverity, str] = {
    "informational": "ℹ️ info",
    "warning": "🟡 warning",
    "critical": "🔴 critical",
}


def _chart_html(
    y_true: np.ndarray, y_score: np.ndarray, sensitive: np.ndarray, title: str, kind: str
) -> str:
    """Render a per-group ROC or reliability chart to a self-contained HTML div."""
    import plotly.graph_objects as go

    fig = go.Figure()
    for g in [str(x) for x in np.unique(sensitive)]:
        m = sensitive == g
        if not np.any(m):
            continue
        if kind == "roc":
            fpr, tpr = roc_curve(y_true[m], y_score[m])
            fig.add_trace(go.Scatter(x=fpr, y=tpr, mode="lines", name=str(g)))
        else:
            xp, yp = reliability_curve(y_true[m], y_score[m])
            fig.add_trace(go.Scatter(x=xp, y=yp, mode="lines+markers", name=str(g)))
    if kind == "roc":
        fig.add_trace(
            go.Scatter(x=[0, 1], y=[0, 1], mode="lines", name="chance", line={"dash": "dot"})
        )
        fig.update_layout(xaxis_title="False positive rate", yaxis_title="True positive rate")
    else:
        fig.add_trace(
            go.Scatter(x=[0, 1], y=[0, 1], mode="lines", name="perfect", line={"dash": "dot"})
        )
        fig.update_layout(xaxis_title="Mean predicted", yaxis_title="Observed frequency")
    fig.update_layout(title=title, height=360, margin={"t": 40, "b": 40, "l": 40, "r": 10})
    return fig.to_html(full_html=False, include_plotlyjs="cdn")  # type: ignore[no-any-return]


def render_report_html(
    report: FairnessReport,
    *,
    y_true: npt.ArrayLike | None = None,
    y_score: npt.ArrayLike | None = None,
    chart_sensitive: np.ndarray | None = None,
    chart_slice_name: str = "",
) -> str:
    """Render the fairness report to a self-contained HTML string."""
    import jinja2

    template_dir = Path(__file__).parent / "templates"
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(template_dir)),
        autoescape=jinja2.select_autoescape(enabled_extensions=("html.j2",)),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    roc_div = reliability_div = ""
    if y_true is not None and y_score is not None and chart_sensitive is not None:
        yt = np.asarray(y_true, dtype=np.int_)
        ys = np.asarray(y_score, dtype=np.float64)
        roc_div = _chart_html(yt, ys, chart_sensitive, f"ROC by {chart_slice_name}", "roc")
        reliability_div = _chart_html(
            yt, ys, chart_sensitive, f"Calibration by {chart_slice_name}", "reliability"
        )

    template = env.get_template("fairness_report.html.j2")
    return template.render(
        r=report,
        badge=_SEVERITY_BADGE,
        roc_div=roc_div,
        reliability_div=reliability_div,
    )


def metric_results_for_slice(
    y_true: npt.ArrayLike,
    y_pred: npt.ArrayLike,
    y_score: npt.ArrayLike,
    sensitive: np.ndarray,
    n_boot: int = 200,
    seed: int = 12345,
) -> dict[str, MetricResult]:
    """Convenience pass-through to :func:`compute_metrics` for a single slice."""
    return compute_metrics(y_true, y_pred, y_score, sensitive, n_boot=n_boot, seed=seed)
