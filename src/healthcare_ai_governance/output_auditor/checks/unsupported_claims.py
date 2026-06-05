"""Unsupported-claims check — LLM as judge (.spec §6.5).

Given an output and its grounding context, asks a strong model to enumerate
claims not supported by the context. Degrades to an informational finding when
no context is available or no LLM client is configured, and to a warning finding
(never a crash) if the judge errors or returns malformed output.
"""

from __future__ import annotations

from healthcare_ai_governance.output_auditor.schema import AuditFinding, LLMOutput
from healthcare_ai_governance.shared.llm_client import LLMClient, parse_json_response
from healthcare_ai_governance.types import FindingSeverity

_SYSTEM = (
    "You are a clinical documentation auditor. Given an AI OUTPUT and its source "
    "CONTEXT, list any factual claims in the OUTPUT that are not directly supported "
    "by the CONTEXT. Respond ONLY with JSON: "
    '{"unsupported_claims": ["claim 1", ...]}. Empty list if all claims are supported.'
)


def _excerpt(text: str, limit: int = 160) -> str:
    return text if len(text) <= limit else text[: limit - 1] + "…"


class UnsupportedClaimsCheck:
    name = "unsupported_claims"
    severity_on_match: FindingSeverity = "warning"

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self._client = llm_client

    def _info(self, output: LLMOutput, explanation: str) -> list[AuditFinding]:
        return [
            AuditFinding(
                check_name=self.name,
                severity="info",
                output_id=output.id,
                excerpt=_excerpt(output.text),
                explanation=explanation,
            )
        ]

    def evaluate(self, output: LLMOutput) -> list[AuditFinding]:
        if not output.context:
            return self._info(output, "No context provided; output could not be verified.")
        if self._client is None:
            return self._info(output, "LLM judge unavailable; output could not be verified.")

        prompt = "CONTEXT:\n" + "\n---\n".join(output.context) + "\n\nOUTPUT:\n" + output.text
        try:
            raw = self._client.complete(_SYSTEM, prompt)
            data = parse_json_response(raw)
            claims = data.get("unsupported_claims", [])
            if not isinstance(claims, list):
                raise ValueError("'unsupported_claims' was not a list")
        except Exception as exc:  # noqa: BLE001 - any judge failure degrades gracefully
            return [
                AuditFinding(
                    check_name=self.name,
                    severity="warning",
                    output_id=output.id,
                    excerpt=_excerpt(output.text),
                    explanation=f"LLM judge could not be parsed ({exc}); manual review advised.",
                )
            ]

        return [
            AuditFinding(
                check_name=self.name,
                severity=self.severity_on_match,
                output_id=output.id,
                excerpt=_excerpt(str(claim)),
                explanation="Claim not supported by the provided context.",
            )
            for claim in claims
        ]
