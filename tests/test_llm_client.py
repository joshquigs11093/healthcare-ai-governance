"""Tests for the LLM client helper (.spec §6.5)."""

from __future__ import annotations

import pytest

from healthcare_ai_governance.config import Settings
from healthcare_ai_governance.shared.llm_client import get_llm_client, parse_json_response


def test_parse_plain_json() -> None:
    assert parse_json_response('{"a": 1}') == {"a": 1}


def test_parse_json_in_prose_and_fences() -> None:
    text = 'Here you go:\n```json\n{"jailbroken": false, "reason": "ok"}\n```'
    assert parse_json_response(text) == {"jailbroken": False, "reason": "ok"}


def test_parse_no_json_raises() -> None:
    with pytest.raises(ValueError, match="No JSON object"):
        parse_json_response("just text, no object")


def test_parse_malformed_json_raises() -> None:
    with pytest.raises(ValueError, match="Malformed JSON"):
        parse_json_response('{"a": }')


def test_get_llm_client_none_without_key() -> None:
    settings = Settings(llm_provider="anthropic", anthropic_api_key=None)
    assert get_llm_client(settings) is None


def test_get_llm_client_none_for_openai_without_key() -> None:
    settings = Settings(llm_provider="openai", openai_api_key=None)
    assert get_llm_client(settings) is None
