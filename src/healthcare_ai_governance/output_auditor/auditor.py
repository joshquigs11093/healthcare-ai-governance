"""Output auditor orchestrator (.spec §6.5)."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import yaml

from healthcare_ai_governance.config import get_settings
from healthcare_ai_governance.output_auditor.checks.citation_validity import CitationValidityCheck
from healthcare_ai_governance.output_auditor.checks.jailbreak import JailbreakCheck
from healthcare_ai_governance.output_auditor.checks.phi_leakage import PHILeakageCheck
from healthcare_ai_governance.output_auditor.checks.tone import ToneCheck
from healthcare_ai_governance.output_auditor.checks.unsupported_claims import (
    UnsupportedClaimsCheck,
)
from healthcare_ai_governance.output_auditor.schema import (
    AuditConfig,
    AuditFinding,
    AuditReport,
    Check,
    LLMOutput,
)
from healthcare_ai_governance.shared.llm_client import LLMClient, get_llm_client
from healthcare_ai_governance.types import FINDING_SEVERITY_ORDER, FindingSeverity, GovernanceError


def build_default_checks(config: AuditConfig, llm_client: LLMClient | None = None) -> list[Check]:
    """Instantiate the enabled checks from config, wiring the LLM client where used."""
    available: dict[str, Check] = {
        "phi_leakage": PHILeakageCheck(config),
        "unsupported_claims": UnsupportedClaimsCheck(llm_client if config.use_llm_judge else None),
        "jailbreak": JailbreakCheck(llm_client=llm_client if config.use_llm_judge else None),
        "tone": ToneCheck(config.prohibited_tone_patterns),
        "citation_validity": CitationValidityCheck(),
    }
    return [available[name] for name in config.enabled_checks if name in available]


class OutputAuditor:
    def __init__(self, checks: list[Check], config: AuditConfig) -> None:
        self._checks = checks
        self._config = config

    @classmethod
    def from_config_file(cls, path: Path) -> OutputAuditor:
        if not path.is_file():
            raise GovernanceError(f"Audit config not found: {path}")
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        config = AuditConfig.model_validate(data)
        llm_client = get_llm_client(get_settings()) if config.use_llm_judge else None
        return cls(build_default_checks(config, llm_client), config)

    def audit(self, outputs: list[LLMOutput]) -> AuditReport:
        findings: dict[str, list[AuditFinding]] = {check.name: [] for check in self._checks}
        for output in outputs:
            for check in self._checks:
                findings[check.name].extend(check.evaluate(output))

        fail_threshold = FINDING_SEVERITY_ORDER[self._config.fail_on]
        overall_pass = not any(
            FINDING_SEVERITY_ORDER[f.severity] >= fail_threshold
            for check_findings in findings.values()
            for f in check_findings
        )
        return AuditReport(
            system_id=self._config.system_id,
            audit_date=date.today(),
            n_outputs_audited=len(outputs),
            checks_run=[check.name for check in self._checks],
            findings=findings,
            overall_pass=overall_pass,
        )

    @property
    def fail_on(self) -> FindingSeverity:
        return self._config.fail_on
