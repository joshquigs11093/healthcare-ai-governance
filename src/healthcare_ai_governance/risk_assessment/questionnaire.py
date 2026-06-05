"""Load and query the risk assessment questionnaire (.spec §6.3)."""

from __future__ import annotations

from collections.abc import Mapping
from functools import lru_cache
from pathlib import Path

import yaml
from pydantic import ValidationError

from healthcare_ai_governance.risk_assessment.schema import RiskQuestion
from healthcare_ai_governance.types import GovernanceError

# The screening question whose "yes" answer activates the Generative AI Profile.
SCREENING_QUESTION_ID = "model.is_generative"

_DEFAULT_PATH = Path(__file__).resolve().parents[3] / "data" / "questionnaire.yaml"


def load_questionnaire(path: Path | None = None) -> list[RiskQuestion]:
    """Load and validate the questionnaire from YAML.

    Raises ``GovernanceError`` on a malformed file, an invalid question, or a
    duplicate question id.
    """
    source = path or _DEFAULT_PATH
    if not source.is_file():
        raise GovernanceError(f"Questionnaire not found: {source}")
    data = yaml.safe_load(source.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or "questions" not in data:
        raise GovernanceError(f"Questionnaire must be a mapping with a 'questions' key: {source}")

    questions: list[RiskQuestion] = []
    seen: set[str] = set()
    for i, raw in enumerate(data["questions"]):
        try:
            q = RiskQuestion.model_validate(raw)
        except ValidationError as exc:
            err = exc.errors()[0]
            loc = ".".join(str(p) for p in err["loc"]) or "<root>"
            raise GovernanceError(
                f"Invalid question at index {i} ({loc}: {err['msg']}) in {source}"
            ) from exc
        if q.id in seen:
            raise GovernanceError(f"Duplicate question id '{q.id}' in {source}")
        seen.add(q.id)
        questions.append(q)
    return questions


@lru_cache(maxsize=1)
def default_questionnaire() -> tuple[RiskQuestion, ...]:
    """Cached load of the bundled questionnaire (immutable tuple)."""
    return tuple(load_questionnaire())


def is_generative_response(responses: Mapping[str, object]) -> bool:
    """Return True if the screening question marks the system as generative."""
    return str(responses.get(SCREENING_QUESTION_ID, "")).lower() == "yes"


def applicable_questions(
    questionnaire: list[RiskQuestion], *, is_generative: bool
) -> list[RiskQuestion]:
    """Filter out generative-only questions when the system is not generative."""
    return [q for q in questionnaire if is_generative or not q.generative_only]
