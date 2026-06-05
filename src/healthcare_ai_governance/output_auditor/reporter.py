"""Summarize audit reports (.spec §6.5)."""

from __future__ import annotations

from healthcare_ai_governance.output_auditor.schema import AuditReport
from healthcare_ai_governance.types import FindingSeverity


def severity_counts(report: AuditReport) -> dict[FindingSeverity, int]:
    """Count findings by severity across all checks."""
    counts: dict[FindingSeverity, int] = {"info": 0, "warning": 0, "error": 0, "critical": 0}
    for check_findings in report.findings.values():
        for f in check_findings:
            counts[f.severity] += 1
    return counts


def summarize(report: AuditReport) -> str:
    """One-line human summary of an audit report."""
    counts = severity_counts(report)
    parts = ", ".join(f"{n} {sev}" for sev, n in counts.items() if n)
    status = "PASS" if report.overall_pass else "FAIL"
    return (
        f"[{status}] {report.system_id}: {report.n_outputs_audited} output(s), "
        f"{sum(counts.values())} finding(s)" + (f" ({parts})" if parts else "")
    )
