"""Fairness and bias evaluation (.spec §6.4).

Metrics are implemented directly in numpy for transparency and auditability
(every computation is inspectable), following the standard fairlearn definitions
of demographic parity, equalized odds, equal opportunity, calibration, and
predictive-value parity. The Synthea-based demo pipeline
(``scripts/generate_fairness_demo.py``) uses scikit-learn to train the model it
evaluates.
"""

from healthcare_ai_governance.fairness.schema import DisparityFlag, FairnessReport

__all__ = ["DisparityFlag", "FairnessReport"]
