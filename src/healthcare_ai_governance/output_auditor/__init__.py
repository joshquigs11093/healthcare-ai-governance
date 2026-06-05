"""LLM output auditor (.spec §6.5).

Combines Microsoft Presidio PII detection (with custom HIPAA recognizers),
LLM-as-judge checks for unsupported claims and citation validity, jailbreak
pattern matching, and configurable tone checks.
"""

from healthcare_ai_governance.output_auditor.schema import (
    AuditConfig,
    AuditFinding,
    AuditReport,
    LLMOutput,
)

__all__ = ["AuditConfig", "AuditFinding", "AuditReport", "LLMOutput"]
