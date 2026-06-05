"""Fairness metrics with bootstrap confidence intervals (.spec §6.4).

Implemented directly in numpy so every computation is auditable. Definitions
follow fairlearn:

- Demographic parity difference: max - min of the selection rate across groups.
- Equalized odds difference: max of (TPR difference, FPR difference) across groups.
- Equal opportunity difference: max - min of the true-positive rate across groups.
- Predictive value parity difference: max - min of the positive predictive value.
- Calibration: Brier score per group (lower is better).

Each disparity metric is returned with a bootstrap 95% confidence interval
(1000 resamples by default; seeded for reproducibility).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

import numpy as np
import numpy.typing as npt

FloatArray = npt.NDArray[np.float64]
IntArray = npt.NDArray[np.int_]

# Disparity-magnitude thresholds for severity tiers (.spec §6.4; configurable).
WARNING_THRESHOLD = 0.05
CRITICAL_THRESHOLD = 0.10

DEFAULT_BOOTSTRAP = 1000


@dataclass
class MetricResult:
    """A single fairness metric: the disparity magnitude, per-group values, CI."""

    name: str
    magnitude: float
    by_group: dict[str, float]
    confidence_interval: tuple[float, float] = (float("nan"), float("nan"))
    disparate_groups: list[str] = field(default_factory=list)


def _as_int(a: npt.ArrayLike) -> IntArray:
    return np.asarray(a, dtype=np.int_)


def _as_float(a: npt.ArrayLike) -> FloatArray:
    return np.asarray(a, dtype=np.float64)


def _groups(sensitive: np.ndarray) -> list[str]:
    return [str(g) for g in np.unique(sensitive)]


def _rate(mask_num: np.ndarray, mask_den: np.ndarray) -> float:
    """Fraction of items in ``mask_den`` that are also in ``mask_num``."""
    den = int(np.sum(mask_den))
    if den == 0:
        return float("nan")
    return float(np.sum(mask_num & mask_den) / den)


def selection_rate_by_group(y_pred: npt.ArrayLike, sensitive: np.ndarray) -> dict[str, float]:
    yp = _as_int(y_pred).astype(bool)
    return {
        g: float(np.mean(yp[sensitive == g])) if np.any(sensitive == g) else float("nan")
        for g in _groups(sensitive)
    }


def tpr_by_group(
    y_true: npt.ArrayLike, y_pred: npt.ArrayLike, sensitive: np.ndarray
) -> dict[str, float]:
    yt, yp = _as_int(y_true).astype(bool), _as_int(y_pred).astype(bool)
    return {g: _rate(yp, yt & (sensitive == g)) for g in _groups(sensitive)}


def fpr_by_group(
    y_true: npt.ArrayLike, y_pred: npt.ArrayLike, sensitive: np.ndarray
) -> dict[str, float]:
    yt, yp = _as_int(y_true).astype(bool), _as_int(y_pred).astype(bool)
    return {g: _rate(yp, ~yt & (sensitive == g)) for g in _groups(sensitive)}


def ppv_by_group(
    y_true: npt.ArrayLike, y_pred: npt.ArrayLike, sensitive: np.ndarray
) -> dict[str, float]:
    yt, yp = _as_int(y_true).astype(bool), _as_int(y_pred).astype(bool)
    return {g: _rate(yt, yp & (sensitive == g)) for g in _groups(sensitive)}


def brier_by_group(
    y_true: npt.ArrayLike, y_score: npt.ArrayLike, sensitive: np.ndarray
) -> dict[str, float]:
    yt, ys = _as_float(y_true), _as_float(y_score)
    out: dict[str, float] = {}
    for g in _groups(sensitive):
        m = sensitive == g
        out[g] = float(np.mean((ys[m] - yt[m]) ** 2)) if np.any(m) else float("nan")
    return out


def _spread(by_group: dict[str, float]) -> tuple[float, list[str]]:
    """Max-min spread of a per-group metric and the two extreme groups."""
    valid = {g: v for g, v in by_group.items() if not np.isnan(v)}
    if len(valid) < 2:
        return 0.0, list(valid)
    hi_g = max(valid, key=lambda g: valid[g])
    lo_g = min(valid, key=lambda g: valid[g])
    return valid[hi_g] - valid[lo_g], [lo_g, hi_g]


def demographic_parity_difference(y_pred: npt.ArrayLike, sensitive: np.ndarray) -> float:
    return _spread(selection_rate_by_group(y_pred, sensitive))[0]


def equal_opportunity_difference(
    y_true: npt.ArrayLike, y_pred: npt.ArrayLike, sensitive: np.ndarray
) -> float:
    return _spread(tpr_by_group(y_true, y_pred, sensitive))[0]


def ppv_parity_difference(
    y_true: npt.ArrayLike, y_pred: npt.ArrayLike, sensitive: np.ndarray
) -> float:
    return _spread(ppv_by_group(y_true, y_pred, sensitive))[0]


def equalized_odds_difference(
    y_true: npt.ArrayLike, y_pred: npt.ArrayLike, sensitive: np.ndarray
) -> float:
    tpr_spread = _spread(tpr_by_group(y_true, y_pred, sensitive))[0]
    fpr_spread = _spread(fpr_by_group(y_true, y_pred, sensitive))[0]
    return max(tpr_spread, fpr_spread)


def _bootstrap_ci(
    statistic: Callable[[IntArray], float],
    n: int,
    n_boot: int,
    seed: int,
    confidence: float = 0.95,
) -> tuple[float, float]:
    """Percentile bootstrap CI for a statistic over resampled row indices."""
    if n == 0:
        return (float("nan"), float("nan"))
    rng = np.random.default_rng(seed)
    samples = np.empty(n_boot, dtype=np.float64)
    for i in range(n_boot):
        idx = rng.integers(0, n, size=n)
        samples[i] = statistic(idx)
    samples = samples[~np.isnan(samples)]
    if samples.size == 0:
        return (float("nan"), float("nan"))
    alpha = (1.0 - confidence) / 2.0
    lo = float(np.percentile(samples, alpha * 100))
    hi = float(np.percentile(samples, (1.0 - alpha) * 100))
    return (lo, hi)


def severity_for(magnitude: float) -> str:
    """Map a disparity magnitude to a severity tier (.spec §6.4)."""
    m = abs(magnitude)
    if m > CRITICAL_THRESHOLD:
        return "critical"
    if m > WARNING_THRESHOLD:
        return "warning"
    return "informational"


def compute_metrics(
    y_true: npt.ArrayLike,
    y_pred: npt.ArrayLike,
    y_score: npt.ArrayLike,
    sensitive: npt.ArrayLike,
    *,
    n_boot: int = DEFAULT_BOOTSTRAP,
    seed: int = 12345,
) -> dict[str, MetricResult]:
    """Compute all fairness metrics for one slice with bootstrap CIs."""
    yt = _as_int(y_true)
    yp = _as_int(y_pred)
    ys = _as_float(y_score)
    sens = np.asarray(sensitive)
    n = len(yt)

    def make(
        name: str,
        by_group: dict[str, float],
        magnitude: float,
        groups: list[str],
        stat: Callable[[IntArray], float],
    ) -> MetricResult:
        ci = _bootstrap_ci(stat, n, n_boot, seed)
        return MetricResult(name, magnitude, by_group, ci, groups)

    dp_groups = selection_rate_by_group(yp, sens)
    dp_mag, dp_extreme = _spread(dp_groups)
    eo_tpr = tpr_by_group(yt, yp, sens)
    eo_mag, eo_extreme = _spread(eo_tpr)
    ppv_groups = ppv_by_group(yt, yp, sens)
    ppv_mag, ppv_extreme = _spread(ppv_groups)
    eodds_mag = equalized_odds_difference(yt, yp, sens)
    eodds_extreme = _spread(eo_tpr)[1]

    return {
        "demographic_parity": make(
            "demographic_parity",
            dp_groups,
            dp_mag,
            dp_extreme,
            lambda idx: demographic_parity_difference(yp[idx], sens[idx]),
        ),
        "equal_opportunity": make(
            "equal_opportunity",
            eo_tpr,
            eo_mag,
            eo_extreme,
            lambda idx: equal_opportunity_difference(yt[idx], yp[idx], sens[idx]),
        ),
        "equalized_odds": make(
            "equalized_odds",
            eo_tpr,
            eodds_mag,
            eodds_extreme,
            lambda idx: equalized_odds_difference(yt[idx], yp[idx], sens[idx]),
        ),
        "ppv_parity": make(
            "ppv_parity",
            ppv_groups,
            ppv_mag,
            ppv_extreme,
            lambda idx: ppv_parity_difference(yt[idx], yp[idx], sens[idx]),
        ),
        "brier_by_group": MetricResult(
            "brier_by_group",
            _spread(brier_by_group(yt, ys, sens))[0],
            brier_by_group(yt, ys, sens),
            (float("nan"), float("nan")),
            _spread(brier_by_group(yt, ys, sens))[1],
        ),
    }
