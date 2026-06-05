"""Tests for fairness metrics, verified with hand-computed values (.spec §9)."""

from __future__ import annotations

import math

import numpy as np
import pytest

from healthcare_ai_governance.fairness.metrics import (
    compute_metrics,
    demographic_parity_difference,
    equal_opportunity_difference,
    equalized_odds_difference,
    ppv_parity_difference,
    selection_rate_by_group,
    severity_for,
)

# A = first 4 rows, B = last 4 rows.
Y_TRUE = np.array([1, 1, 0, 0, 1, 1, 0, 0])
Y_PRED = np.array([1, 0, 0, 0, 1, 1, 1, 0])
SENS = np.array(["A", "A", "A", "A", "B", "B", "B", "B"])
Y_SCORE = np.array([0.9, 0.4, 0.2, 0.1, 0.8, 0.7, 0.6, 0.3])


def test_selection_rate_by_group() -> None:
    rates = selection_rate_by_group(Y_PRED, SENS)
    assert rates["A"] == pytest.approx(0.25)
    assert rates["B"] == pytest.approx(0.75)


def test_demographic_parity_difference() -> None:
    assert demographic_parity_difference(Y_PRED, SENS) == pytest.approx(0.5)


def test_equal_opportunity_difference() -> None:
    # TPR A = 1/2 = 0.5, TPR B = 2/2 = 1.0 -> diff 0.5
    assert equal_opportunity_difference(Y_TRUE, Y_PRED, SENS) == pytest.approx(0.5)


def test_equalized_odds_difference() -> None:
    # TPR diff 0.5, FPR diff 0.5 -> max 0.5
    assert equalized_odds_difference(Y_TRUE, Y_PRED, SENS) == pytest.approx(0.5)


def test_ppv_parity_difference() -> None:
    # PPV A = 1/1 = 1.0, PPV B = 2/3 -> diff 1/3
    assert ppv_parity_difference(Y_TRUE, Y_PRED, SENS) == pytest.approx(1 / 3)


def test_compute_metrics_bundles_results_with_ci() -> None:
    results = compute_metrics(Y_TRUE, Y_PRED, Y_SCORE, SENS, n_boot=50, seed=1)
    assert results["demographic_parity"].magnitude == pytest.approx(0.5)
    assert results["demographic_parity"].disparate_groups == ["A", "B"]
    lo, hi = results["demographic_parity"].confidence_interval
    assert lo <= hi
    assert not math.isnan(results["brier_by_group"].magnitude)


@pytest.mark.parametrize(
    ("magnitude", "expected"),
    [(0.0, "informational"), (0.05, "informational"), (0.06, "warning"), (0.11, "critical")],
)
def test_severity_thresholds(magnitude: float, expected: str) -> None:
    assert severity_for(magnitude) == expected


def test_single_group_has_zero_disparity() -> None:
    sens = np.array(["A", "A", "A", "A"])
    assert demographic_parity_difference(np.array([1, 0, 1, 0]), sens) == 0.0
