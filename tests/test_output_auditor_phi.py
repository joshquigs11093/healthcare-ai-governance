"""PHI leakage detection tests (.spec §9).

Verifies the custom regex recognizers detect the pattern-detectable HIPAA
identifiers, and that non-PHI clinical narrative does not false-positive. Names,
geographic subdivisions, and other NER-based identifiers require Presidio and are
covered in the Docker/CI environment.
"""

from __future__ import annotations

from healthcare_ai_governance.output_auditor.checks.phi_leakage import PHILeakageCheck
from healthcare_ai_governance.output_auditor.schema import AuditConfig, LLMOutput

# Synthetic clinical text containing one of each regex-detectable identifier.
_PHI_SAMPLES = {
    "US_SSN": "SSN is 123-45-6789.",
    "EMAIL": "Contact jane.doe@example.com for records.",
    "URL": "See https://patient.example.org/chart for details.",
    "IP_ADDRESS": "Logged from 192.168.1.45 last night.",
    "PHONE_FAX": "Call the clinic at (617) 555-0142.",
    "MRN": "Patient MRN: 0048221 admitted today.",
    "ACCOUNT_NUMBER": "Billing account #: 99381720 is past due.",
    "HEALTH_PLAN_ID": "Member ID: ABCD1234 on file.",
    "LICENSE_NUMBER": "Provider license: MD123456 verified.",
    "DEVICE_ID": "Pacemaker serial: AB12345XZ implanted.",
    "VIN": "Transport vehicle VIN 1HGCM82633A004352 noted.",
    "DATE": "Date of service 03/14/2026 recorded.",
    "ZIP_PLUS4": "Home ZIP 02115-1234 listed.",
    "AGE_OVER_89": "The patient is 92 years old.",
}

_CLEAN_CLINICAL = (
    "The patient presented with acute pyelonephritis and costovertebral angle "
    "tenderness. Plan: continue ceftriaxone, monitor renal function, and reassess "
    "in the morning. CBC showed leukocytosis; lactate was within normal limits. "
    "Differential includes nephrolithiasis. Device placement was uncomplicated and "
    "the certificate of medical necessity is on file."
)


def _entities(text: str) -> set[str]:
    check = PHILeakageCheck(use_presidio=False)
    findings = check.evaluate(LLMOutput(id="o1", text=text))
    # Entity type is embedded in the redacted excerpt as [ENTITY].
    return {f.explanation.split("Possible ")[1].split(" PHI")[0] for f in findings}


def test_each_phi_type_detected() -> None:
    for expected_entity, text in _PHI_SAMPLES.items():
        entities = _entities(text)
        assert expected_entity in entities, f"{expected_entity} not detected in: {text!r}"


def test_clean_clinical_text_no_false_positives() -> None:
    check = PHILeakageCheck(use_presidio=False)
    findings = check.evaluate(LLMOutput(id="clean", text=_CLEAN_CLINICAL))
    assert findings == [], f"unexpected PHI findings: {[f.explanation for f in findings]}"


def test_redacted_excerpt_hides_value() -> None:
    check = PHILeakageCheck(use_presidio=False)
    findings = check.evaluate(LLMOutput(id="o", text="SSN is 123-45-6789 today."))
    assert findings
    assert "123-45-6789" not in findings[0].excerpt
    assert "[US_SSN]" in findings[0].excerpt


def test_custom_mrn_pattern_from_config() -> None:
    config = AuditConfig(mrn_patterns=[r"\bZ\d{7}\b"])
    check = PHILeakageCheck(config, use_presidio=False)
    findings = check.evaluate(LLMOutput(id="o", text="Record Z1234567 pulled."))
    assert any("MRN" in f.explanation for f in findings)
