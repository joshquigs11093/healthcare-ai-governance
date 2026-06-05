"""Tone check (.spec §6.5).

Configurable per system. Example: for a system documented as "informational
only, not decision support," flag outputs containing definitive medical
recommendations. Patterns come from the audit config (``prohibited_tone_patterns``).
"""

from __future__ import annotations

import re

from healthcare_ai_governance.output_auditor.schema import AuditFinding, LLMOutput
from healthcare_ai_governance.types import FindingSeverity

# Sensible defaults for an "informational only" system; overridable via config.
_DEFAULT_PATTERNS = (
    r"you should take",
    r"the correct treatment is",
    r"i recommend (?:that you|starting)",
    r"you must stop taking",
    r"the diagnosis is",
)


class ToneCheck:
    name = "tone"
    severity_on_match: FindingSeverity = "warning"

    def __init__(self, patterns: list[str] | None = None) -> None:
        source = patterns if patterns else list(_DEFAULT_PATTERNS)
        self._patterns = [re.compile(p, re.IGNORECASE) for p in source]

    def evaluate(self, output: LLMOutput) -> list[AuditFinding]:
        findings: list[AuditFinding] = []
        for pat in self._patterns:
            m = pat.search(output.text)
            if m:
                findings.append(
                    AuditFinding(
                        check_name=self.name,
                        severity=self.severity_on_match,
                        output_id=output.id,
                        excerpt=output.text[max(0, m.start() - 20) : m.end() + 20],
                        explanation=(
                            f"Output uses prescriptive language ('{m.group(0)}') that may exceed "
                            "the system's documented informational-only scope."
                        ),
                    )
                )
        return findings
