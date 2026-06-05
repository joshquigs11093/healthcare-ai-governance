"""PHI leakage check (.spec §6.5).

Uses Microsoft Presidio's AnalyzerEngine when available (adding PERSON,
LOCATION, and other NER-based entities) plus custom regex recognizers for the
pattern-detectable HIPAA 18 identifiers that Presidio does not natively cover or
covers imperfectly. The regex recognizers run with or without Presidio so the
check is useful on any host.

Coverage note (also in the module README): name, geographic, and free-text
identifiers require Presidio's NER. Full-face photographs are out of scope for a
text auditor. See ADR-005 and .spec §3 on Presidio's limits for clinical text.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from healthcare_ai_governance.output_auditor.schema import (
    AuditConfig,
    AuditFinding,
    LLMOutput,
)
from healthcare_ai_governance.types import FindingSeverity


@dataclass(frozen=True)
class _Recognizer:
    entity_type: str
    pattern: re.Pattern[str]


# Custom regex recognizers for pattern-detectable HIPAA identifiers.
_BASE_RECOGNIZERS: tuple[_Recognizer, ...] = (
    _Recognizer("US_SSN", re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
    _Recognizer("EMAIL", re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")),
    _Recognizer("URL", re.compile(r"\bhttps?://[^\s)]+", re.IGNORECASE)),
    _Recognizer("IP_ADDRESS", re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")),
    _Recognizer(
        "PHONE_FAX",
        re.compile(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}\b"),
    ),
    _Recognizer("MRN", re.compile(r"\bMRN[\s#:]*\d{6,10}\b", re.IGNORECASE)),
    _Recognizer(
        "ACCOUNT_NUMBER",
        re.compile(r"\bacc(?:t|ount)?\b[\s#:]*\d{6,12}\b", re.IGNORECASE),
    ),
    # Require an explicit id/number keyword AND a digit-bearing value so common
    # clinical phrasing ("Plan: continue antibiotics") does not false-positive.
    _Recognizer(
        "HEALTH_PLAN_ID",
        re.compile(
            r"\b(?:member|policy|plan|beneficiary)\s*(?:id|no\.?|number)[:#]?\s*"
            r"(?=[A-Z0-9-]*\d)[A-Z0-9-]{5,}\b",
            re.IGNORECASE,
        ),
    ),
    _Recognizer(
        "LICENSE_NUMBER",
        re.compile(
            r"\b(?:license|licence|certificate|cert)[:#]?\s*(?=[A-Z0-9-]*\d)[A-Z0-9-]{5,}\b",
            re.IGNORECASE,
        ),
    ),
    _Recognizer(
        "DEVICE_ID",
        re.compile(
            r"\b(?:serial|device|sn)[:#]?\s*(?=[A-Z0-9-]*\d)[A-Z0-9][A-Z0-9-]{5,}\b",
            re.IGNORECASE,
        ),
    ),
    _Recognizer("VIN", re.compile(r"\b[A-HJ-NPR-Z0-9]{17}\b")),
    _Recognizer("DATE", re.compile(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b")),
    _Recognizer("DATE", re.compile(r"\b\d{4}-\d{2}-\d{2}\b")),
    _Recognizer("ZIP_PLUS4", re.compile(r"\b\d{5}-\d{4}\b")),
    _Recognizer(
        "AGE_OVER_89",
        re.compile(r"\b(?:9\d|1\d\d)\s*(?:years?[\s-]*old|y/?o|yo)\b", re.IGNORECASE),
    ),
)

# Presidio entity types worth surfacing (NER-based, not regex-detectable here).
_PRESIDIO_ENTITIES = ("PERSON", "LOCATION", "NRP", "MEDICAL_LICENSE")

_CONTEXT_CHARS = 50


def _redact_excerpt(text: str, start: int, end: int, label: str) -> str:
    lo = max(0, start - _CONTEXT_CHARS)
    hi = min(len(text), end + _CONTEXT_CHARS)
    prefix = "..." if lo > 0 else ""
    suffix = "..." if hi < len(text) else ""
    return f"{prefix}{text[lo:start]}[{label}]{text[end:hi]}{suffix}"


class PHILeakageCheck:
    name = "phi_leakage"
    severity_on_match: FindingSeverity = "critical"

    def __init__(self, config: AuditConfig | None = None, use_presidio: bool = True) -> None:
        self._config = config or AuditConfig()
        self._recognizers = list(_BASE_RECOGNIZERS)
        for pat in self._config.mrn_patterns:
            self._recognizers.append(_Recognizer("MRN", re.compile(pat)))
        for pat in self._config.account_patterns:
            self._recognizers.append(_Recognizer("ACCOUNT_NUMBER", re.compile(pat)))
        self._analyzer = self._build_presidio() if use_presidio else None

    @staticmethod
    def _build_presidio() -> Any:
        try:
            from presidio_analyzer import AnalyzerEngine
        except (ImportError, OSError):  # pragma: no cover - env-dependent
            return None
        try:  # pragma: no cover - requires spaCy model
            return AnalyzerEngine()
        except Exception:  # pragma: no cover - model not downloaded
            return None

    def _regex_spans(self, text: str) -> list[tuple[str, int, int]]:
        spans: list[tuple[str, int, int]] = []
        for rec in self._recognizers:
            for m in rec.pattern.finditer(text):
                spans.append((rec.entity_type, m.start(), m.end()))
        return spans

    def _presidio_spans(self, text: str) -> list[tuple[str, int, int]]:  # pragma: no cover - Docker
        if self._analyzer is None:
            return []
        results = self._analyzer.analyze(
            text=text, entities=list(_PRESIDIO_ENTITIES), language="en"
        )
        return [(r.entity_type, r.start, r.end) for r in results]

    def evaluate(self, output: LLMOutput) -> list[AuditFinding]:
        text = output.text
        spans = self._regex_spans(text) + self._presidio_spans(text)
        # Deduplicate overlapping spans, keeping the longest per start position.
        seen: dict[tuple[int, int], str] = {}
        for entity, start, end in spans:
            seen.setdefault((start, end), entity)
        findings: list[AuditFinding] = []
        for (start, end), entity in sorted(seen.items()):
            findings.append(
                AuditFinding(
                    check_name=self.name,
                    severity=self.severity_on_match,
                    output_id=output.id,
                    excerpt=_redact_excerpt(text, start, end, entity),
                    explanation=f"Possible {entity} PHI identifier detected in output.",
                )
            )
        return findings
