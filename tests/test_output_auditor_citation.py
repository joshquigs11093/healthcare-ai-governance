"""Citation validity tests (.spec §9)."""

from __future__ import annotations

from healthcare_ai_governance.output_auditor.checks.citation_validity import (
    CitationValidityCheck,
)
from healthcare_ai_governance.output_auditor.schema import LLMOutput


def test_valid_numeric_citation_passes() -> None:
    check = CitationValidityCheck()
    out = LLMOutput(id="o", text="Per guideline [1], start therapy.", context=["Guideline A"])
    assert check.evaluate(out) == []


def test_hallucinated_numeric_citation_flagged() -> None:
    check = CitationValidityCheck()
    out = LLMOutput(id="o", text="See [3] for details.", context=["Only one source"])
    findings = check.evaluate(out)
    assert len(findings) == 1
    assert findings[0].severity == "error"
    assert "[3]" in findings[0].excerpt


def test_numeric_citation_with_no_context_flagged() -> None:
    check = CitationValidityCheck()
    out = LLMOutput(id="o", text="As shown [1].", context=[])
    assert len(check.evaluate(out)) == 1


def test_valid_named_source_passes() -> None:
    check = CitationValidityCheck()
    out = LLMOutput(
        id="o",
        text="[Source: JNC8] recommends this.",
        context=["The JNC8 hypertension guideline says..."],
    )
    assert check.evaluate(out) == []


def test_hallucinated_named_source_flagged() -> None:
    check = CitationValidityCheck()
    out = LLMOutput(
        id="o",
        text="[Source: Fictional Study 2030] proves it.",
        context=["Unrelated source text"],
    )
    findings = check.evaluate(out)
    assert len(findings) == 1
    assert "Fictional Study 2030" in findings[0].explanation
