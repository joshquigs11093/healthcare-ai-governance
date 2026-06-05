"""Map risk patterns to recommended mitigations (.spec §6.3)."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml
from pydantic import BaseModel, Field

from healthcare_ai_governance.risk_assessment.schema import ResponseValue
from healthcare_ai_governance.types import RISK_TIER_ORDER, GovernanceError, RiskTier

_DEFAULT_PATH = Path(__file__).resolve().parents[3] / "data" / "mitigations.yaml"


class _Condition(BaseModel):
    model_config = {"extra": "forbid"}

    responses: dict[str, str | list[str]] = Field(default_factory=dict)
    min_tier: RiskTier | None = None


class MitigationRule(BaseModel):
    model_config = {"extra": "forbid"}

    id: str
    when: _Condition
    mitigation: str
    nist_rmf_subcategory: str

    def matches(self, responses: dict[str, ResponseValue], computed_tier: RiskTier) -> bool:
        if (
            self.when.min_tier is not None
            and RISK_TIER_ORDER[computed_tier] < RISK_TIER_ORDER[self.when.min_tier]
        ):
            return False
        for qid, expected in self.when.responses.items():
            actual = responses.get(qid)
            if actual is None:
                return False
            accepted = expected if isinstance(expected, list) else [expected]
            if isinstance(actual, list):
                # multiselect: fire if any selected value is accepted
                if not any(a in accepted for a in actual):
                    return False
            elif str(actual) not in accepted:
                return False
        return True


def load_mitigation_rules(path: Path | None = None) -> list[MitigationRule]:
    source = path or _DEFAULT_PATH
    if not source.is_file():
        raise GovernanceError(f"Mitigations file not found: {source}")
    data = yaml.safe_load(source.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or "mitigations" not in data:
        raise GovernanceError(f"Mitigations must be a mapping with a 'mitigations' key: {source}")
    return [MitigationRule.model_validate(raw) for raw in data["mitigations"]]


@lru_cache(maxsize=1)
def default_mitigation_rules() -> tuple[MitigationRule, ...]:
    return tuple(load_mitigation_rules())


def recommend_mitigations(
    responses: dict[str, ResponseValue],
    computed_tier: RiskTier,
    rules: list[MitigationRule] | None = None,
) -> list[str]:
    """Return recommended mitigations (NIST-tagged) for the given responses/tier.

    Deterministic and ordered by the rule file; each string is
    ``"<mitigation> (NIST <subcategory>)"``.
    """
    active = rules if rules is not None else list(default_mitigation_rules())
    out: list[str] = []
    for rule in active:
        if rule.matches(responses, computed_tier):
            out.append(f"{rule.mitigation} (NIST {rule.nist_rmf_subcategory})")
    return out
