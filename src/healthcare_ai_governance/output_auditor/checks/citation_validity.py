"""Citation validity check (.spec §6.5).

Catches the common failure mode of hallucinated citations: references in the
output (``[1]``, ``[Source: X]``) that do not correspond to any provided context
source.
"""

from __future__ import annotations

import re

from healthcare_ai_governance.output_auditor.schema import AuditFinding, LLMOutput
from healthcare_ai_governance.types import FindingSeverity

_NUMERIC = re.compile(r"\[(\d{1,3})\]")
_SOURCE = re.compile(r"\[Source:\s*([^\]]+)\]", re.IGNORECASE)


class CitationValidityCheck:
    name = "citation_validity"
    severity_on_match: FindingSeverity = "error"

    def _finding(self, output: LLMOutput, citation: str, why: str) -> AuditFinding:
        return AuditFinding(
            check_name=self.name,
            severity=self.severity_on_match,
            output_id=output.id,
            excerpt=citation,
            explanation=why,
        )

    def evaluate(self, output: LLMOutput) -> list[AuditFinding]:
        findings: list[AuditFinding] = []
        n_context = len(output.context)
        context_blob = "\n".join(output.context).lower()

        for m in _NUMERIC.finditer(output.text):
            idx = int(m.group(1))
            if idx < 1 or idx > n_context:
                findings.append(
                    self._finding(
                        output,
                        m.group(0),
                        f"Citation {m.group(0)} refers to source {idx}, but only "
                        f"{n_context} source(s) were provided.",
                    )
                )

        for m in _SOURCE.finditer(output.text):
            name = m.group(1).strip().lower()
            if name not in context_blob:
                findings.append(
                    self._finding(
                        output,
                        m.group(0),
                        f"Cited source '{m.group(1).strip()}' does not appear in the "
                        "provided context.",
                    )
                )

        return findings
