"""Tests for the fairness slicer and report builder (.spec §9)."""

from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd
import pytest

from healthcare_ai_governance.fairness.reporter import (
    build_report,
    reliability_curve,
    render_report_html,
    roc_curve,
)
from healthcare_ai_governance.fairness.slicer import age_band, build_slices


def test_age_band_labels() -> None:
    ages = pd.Series([10, 25, 50, 70, 85])
    bands = age_band(ages, (18, 40, 65, 80))
    assert list(bands) == ["<18", "18-39", "40-64", "65-79", "80+"]


def test_build_slices_includes_single_and_intersectional() -> None:
    df = pd.DataFrame(
        {
            "age": [30, 70, 50],
            "sex": ["F", "M", "F"],
            "race": ["White", "Black", "White"],
            "payer": ["Medicaid", "Medicare", "Commercial"],
        }
    )
    slices = build_slices(df)
    assert "age_band" in slices
    assert "sex" in slices and "race" in slices and "payer" in slices
    assert "race_x_payer" in slices
    assert "age_band_x_sex" in slices
    assert slices["race_x_payer"][0] == "White / Medicaid"


def test_build_slices_skips_absent_columns() -> None:
    df = pd.DataFrame({"sex": ["F", "M"]})
    slices = build_slices(df)
    assert set(slices) == {"sex"}  # no age, race, payer, or intersectional


def test_roc_curve_monotonic() -> None:
    fpr, tpr = roc_curve([0, 0, 1, 1], [0.1, 0.2, 0.8, 0.9])
    assert fpr[0] == 0.0 and tpr[0] == 0.0
    assert tpr[-1] == pytest.approx(1.0)
    # Perfectly separable -> reaches tpr 1.0 before any false positives.
    assert max(tpr) == pytest.approx(1.0)


def test_roc_curve_degenerate_single_class() -> None:
    fpr, tpr = roc_curve([1, 1, 1], [0.5, 0.6, 0.7])
    assert fpr == [0.0, 1.0] and tpr == [0.0, 1.0]


def test_reliability_curve() -> None:
    xp, yp = reliability_curve([0, 1, 0, 1], [0.1, 0.9, 0.2, 0.8], bins=10)
    assert len(xp) == len(yp)
    assert all(0.0 <= v <= 1.0 for v in yp)


@pytest.fixture
def cohort() -> pd.DataFrame:
    rng = np.random.default_rng(0)
    n = 400
    race = rng.choice(["White", "Black"], size=n)
    return pd.DataFrame(
        {
            "age": rng.integers(20, 85, n),
            "sex": rng.choice(["F", "M"], n),
            "race": race,
            "payer": rng.choice(["Medicare", "Medicaid"], n),
        }
    )


def test_build_report_structure(cohort: pd.DataFrame) -> None:
    n = len(cohort)
    rng = np.random.default_rng(1)
    y_true = rng.integers(0, 2, n)
    # Inject a disparity: White predicted positive far more often than Black.
    y_pred = np.where(cohort["race"].to_numpy() == "White", 1, 0)
    y_score = np.where(cohort["race"].to_numpy() == "White", 0.8, 0.2)
    report = build_report(
        system_id="demo",
        y_true=y_true,
        y_pred=y_pred,
        y_score=y_score,
        df=cohort,
        evaluation_date=date(2026, 1, 1),
        n_boot=50,
    )
    assert report.population_size == n
    assert "race" in report.slices_evaluated
    assert report.metrics_by_slice["race"]["demographic_parity"] > 0.5
    # The race demographic-parity disparity should be flagged as critical.
    race_flags = [f for f in report.disparities_flagged if f.slice_name == "race"]
    assert any(f.severity == "critical" for f in race_flags)


def test_render_report_html(cohort: pd.DataFrame) -> None:
    n = len(cohort)
    y_true = np.random.default_rng(2).integers(0, 2, n)
    y_pred = np.zeros(n, dtype=int)
    y_score = np.full(n, 0.3)
    report = build_report(
        system_id="demo",
        y_true=y_true,
        y_pred=y_pred,
        y_score=y_score,
        df=cohort,
        evaluation_date=date(2026, 1, 1),
        n_boot=20,
    )
    html = render_report_html(
        report,
        y_true=y_true,
        y_score=y_score,
        chart_sensitive=cohort["race"].astype("string").to_numpy(),
        chart_slice_name="race",
    )
    assert "<html" in html.lower()
    assert "AI Fairness" in html
    assert "demo" in html
