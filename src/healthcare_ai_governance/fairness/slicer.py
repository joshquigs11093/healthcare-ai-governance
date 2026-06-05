"""Slicing categories for fairness evaluation (.spec §6.4).

Produces, for each configured slice, a per-row group-label array aligned with the
evaluation dataframe. Slices are only built when their source column(s) exist, so
the evaluator degrades gracefully on partial data.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

# Default age-band cut points (left-closed bins): [18,40), [40,65), [65,80), 80+.
DEFAULT_AGE_CUTS = (18, 40, 65, 80)

# Standard demographic and healthcare-specific single-column slices (.spec §6.4).
_STANDARD_COLUMNS = ("sex", "race")
_HEALTHCARE_COLUMNS = ("payer", "encounter_type", "service_line", "urgency")

# Default intersectional pairs.
DEFAULT_INTERSECTIONAL = (("race", "payer"), ("age_band", "sex"))


@dataclass
class SlicerConfig:
    age_column: str = "age"
    age_cuts: tuple[int, ...] = DEFAULT_AGE_CUTS
    intersectional: tuple[tuple[str, str], ...] = DEFAULT_INTERSECTIONAL
    extra_columns: tuple[str, ...] = field(default_factory=tuple)


def age_band(ages: pd.Series, cuts: tuple[int, ...] = DEFAULT_AGE_CUTS) -> pd.Series:
    """Bucket numeric ages into left-closed band labels (e.g. ``40-64``, ``80+``)."""
    edges = [float("-inf"), *cuts, float("inf")]
    labels: list[str] = []
    for i in range(len(edges) - 1):
        lo, hi = edges[i], edges[i + 1]
        if lo == float("-inf"):
            labels.append(f"<{int(hi)}")
        elif hi == float("inf"):
            labels.append(f"{int(lo)}+")
        else:
            labels.append(f"{int(lo)}-{int(hi) - 1}")
    return pd.cut(ages, bins=edges, labels=labels, right=False).astype("string")


def build_slices(df: pd.DataFrame, config: SlicerConfig | None = None) -> dict[str, np.ndarray]:
    """Return ``{slice_name: group_label_array}`` for every applicable slice."""
    cfg = config or SlicerConfig()
    work = df.copy()
    if cfg.age_column in work.columns:
        work["age_band"] = age_band(work[cfg.age_column], cfg.age_cuts)

    slices: dict[str, np.ndarray] = {}

    single = ["age_band", *_STANDARD_COLUMNS, *_HEALTHCARE_COLUMNS, *cfg.extra_columns]
    for col in single:
        if col in work.columns:
            slices[col] = work[col].astype("string").to_numpy()

    for a, b in cfg.intersectional:
        if a in work.columns and b in work.columns:
            name = f"{a}_x_{b}"
            combined = work[a].astype("string") + " / " + work[b].astype("string")
            slices[name] = combined.to_numpy()

    return slices
