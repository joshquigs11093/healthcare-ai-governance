"""Unsupported-claims (LLM-as-judge) tests with a mocked client (.spec §9)."""

from __future__ import annotations

from healthcare_ai_governance.output_auditor.checks.unsupported_claims import (
    UnsupportedClaimsCheck,
)
from healthcare_ai_governance.output_auditor.schema import LLMOutput


class _FakeClient:
    def __init__(self, response: str) -> None:
        self.response = response
        self.calls = 0

    def complete(self, system: str, prompt: str) -> str:
        self.calls += 1
        return self.response


def _output(**kw: object) -> LLMOutput:
    base = {"id": "o1", "text": "The drug cures cancer.", "context": ["The drug lowers BP."]}
    base.update(kw)
    return LLMOutput.model_validate(base)


def test_no_context_returns_info() -> None:
    check = UnsupportedClaimsCheck(_FakeClient("{}"))
    findings = check.evaluate(_output(context=[]))
    assert len(findings) == 1
    assert findings[0].severity == "info"


def test_no_client_returns_info() -> None:
    check = UnsupportedClaimsCheck(None)
    findings = check.evaluate(_output())
    assert findings[0].severity == "info"
    assert "unavailable" in findings[0].explanation


def test_parses_unsupported_claims() -> None:
    client = _FakeClient('{"unsupported_claims": ["The drug cures cancer."]}')
    check = UnsupportedClaimsCheck(client)
    findings = check.evaluate(_output())
    assert client.calls == 1
    assert len(findings) == 1
    assert findings[0].severity == "warning"
    assert "cures cancer" in findings[0].excerpt


def test_no_unsupported_claims_returns_empty() -> None:
    check = UnsupportedClaimsCheck(_FakeClient('{"unsupported_claims": []}'))
    assert check.evaluate(_output()) == []


def test_handles_prose_wrapped_json() -> None:
    client = _FakeClient('Sure!\n```json\n{"unsupported_claims": ["x"]}\n```')
    check = UnsupportedClaimsCheck(client)
    findings = check.evaluate(_output())
    assert len(findings) == 1


def test_malformed_response_degrades_to_warning() -> None:
    check = UnsupportedClaimsCheck(_FakeClient("not json at all"))
    findings = check.evaluate(_output())
    assert len(findings) == 1
    assert findings[0].severity == "warning"
    assert "could not be parsed" in findings[0].explanation


def test_client_exception_degrades_to_warning() -> None:
    class _Boom:
        def complete(self, system: str, prompt: str) -> str:
            raise RuntimeError("network down")

    check = UnsupportedClaimsCheck(_Boom())
    findings = check.evaluate(_output())
    assert findings[0].severity == "warning"
