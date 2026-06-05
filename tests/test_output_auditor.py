"""Tests for jailbreak/tone checks, the orchestrator, and the audit CLI (.spec §6.5)."""

from __future__ import annotations

import json
from pathlib import Path

import yaml
from typer.testing import CliRunner

from healthcare_ai_governance.cli import app
from healthcare_ai_governance.output_auditor.auditor import OutputAuditor, build_default_checks
from healthcare_ai_governance.output_auditor.checks.jailbreak import JailbreakCheck
from healthcare_ai_governance.output_auditor.checks.tone import ToneCheck
from healthcare_ai_governance.output_auditor.reporter import severity_counts, summarize
from healthcare_ai_governance.output_auditor.schema import AuditConfig, LLMOutput

runner = CliRunner()


def test_jailbreak_pattern_match() -> None:
    check = JailbreakCheck(patterns=("ignore previous instructions",))
    out = LLMOutput(id="o", text="Sure, I will ignore previous instructions and comply.")
    findings = check.evaluate(out)
    assert len(findings) == 1
    assert findings[0].severity == "error"


def test_jailbreak_clean_output() -> None:
    check = JailbreakCheck(patterns=("ignore previous instructions",))
    assert check.evaluate(LLMOutput(id="o", text="Here is the lab summary.")) == []


def test_tone_default_patterns() -> None:
    check = ToneCheck()
    out = LLMOutput(id="o", text="You should take 200mg twice daily.")
    findings = check.evaluate(out)
    assert len(findings) == 1
    assert findings[0].severity == "warning"


def test_tone_custom_patterns() -> None:
    check = ToneCheck(patterns=[r"guaranteed cure"])
    assert check.evaluate(LLMOutput(id="o", text="This is a guaranteed cure.")) != []
    assert check.evaluate(LLMOutput(id="o", text="You should take it.")) == []


def test_orchestrator_groups_findings_and_pass_flag() -> None:
    config = AuditConfig(
        system_id="demo",
        enabled_checks=["phi_leakage", "citation_validity"],
        use_llm_judge=False,
        fail_on="critical",
    )
    auditor = OutputAuditor(build_default_checks(config), config)
    outputs = [
        LLMOutput(id="a", text="SSN 123-45-6789 leaked."),  # critical PHI
        LLMOutput(id="b", text="Clean output."),
    ]
    report = auditor.audit(outputs)
    assert report.n_outputs_audited == 2
    assert set(report.checks_run) == {"phi_leakage", "citation_validity"}
    assert report.findings["phi_leakage"]  # PHI found
    assert report.overall_pass is False  # critical >= fail_on


def test_orchestrator_passes_when_below_threshold() -> None:
    config = AuditConfig(
        system_id="demo", enabled_checks=["tone"], use_llm_judge=False, fail_on="critical"
    )
    auditor = OutputAuditor(build_default_checks(config), config)
    report = auditor.audit([LLMOutput(id="a", text="You should take this.")])
    assert report.findings["tone"]  # warning finding exists
    assert report.overall_pass is True  # warning < critical


def test_reporter_summary() -> None:
    config = AuditConfig(system_id="demo", enabled_checks=["phi_leakage"], use_llm_judge=False)
    auditor = OutputAuditor(build_default_checks(config), config)
    report = auditor.audit([LLMOutput(id="a", text="SSN 123-45-6789.")])
    counts = severity_counts(report)
    assert counts["critical"] >= 1
    assert "demo" in summarize(report)


# ---- CLI ----


def _config_file(tmp_path: Path) -> Path:
    cfg = {
        "system_id": "guideline-gpt",
        "enabled_checks": ["phi_leakage", "citation_validity", "tone"],
        "use_llm_judge": False,
        "fail_on": "critical",
    }
    path = tmp_path / "audit.yaml"
    path.write_text(yaml.safe_dump(cfg), encoding="utf-8")
    return path


def _outputs_file(tmp_path: Path) -> Path:
    rows = [
        {"id": "o1", "text": "Patient SSN 123-45-6789 noted.", "context": []},
        {"id": "o2", "text": "See [5] for the protocol.", "context": ["only one source"]},
    ]
    path = tmp_path / "outputs.jsonl"
    path.write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
    return path


def test_cli_run_writes_report(tmp_path: Path) -> None:
    config = _config_file(tmp_path)
    outputs = _outputs_file(tmp_path)
    out = tmp_path / "reports"
    result = runner.invoke(
        app, ["audit", "run", str(outputs), "--config", str(config), "-o", str(out)]
    )
    assert result.exit_code == 0
    report_files = list(out.glob("guideline-gpt-*.json"))
    assert len(report_files) == 1
    data = json.loads(report_files[0].read_text(encoding="utf-8"))
    assert data["findings"]["phi_leakage"]
    assert data["overall_pass"] is False


def test_cli_ci_fails_on_critical(tmp_path: Path) -> None:
    config = _config_file(tmp_path)
    outputs = _outputs_file(tmp_path)
    result = runner.invoke(
        app, ["audit", "ci", str(outputs), "--config", str(config), "--fail-on", "critical"]
    )
    assert result.exit_code == 1  # SSN PHI is critical


def test_cli_ci_passes_when_threshold_high(tmp_path: Path) -> None:
    # Only a citation error (severity 'error'); fail-on critical -> pass.
    config = _config_file(tmp_path)
    rows = [{"id": "o", "text": "See [9].", "context": ["one source"]}]
    outputs = tmp_path / "o.jsonl"
    outputs.write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
    result = runner.invoke(
        app, ["audit", "ci", str(outputs), "--config", str(config), "--fail-on", "critical"]
    )
    assert result.exit_code == 0
