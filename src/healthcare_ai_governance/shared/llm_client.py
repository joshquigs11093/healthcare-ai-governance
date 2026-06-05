"""LLM provider abstraction for the auditor's LLM-as-judge checks (.spec §3, §6.5).

A minimal ``complete(system, prompt) -> str`` interface with Anthropic and OpenAI
implementations (imported lazily). ``get_llm_client`` returns ``None`` when no
provider is configured, so judge checks degrade to an informational finding
rather than failing.
"""

from __future__ import annotations

import json
import re
from typing import Protocol, runtime_checkable

from healthcare_ai_governance.config import Settings

_JSON_BLOCK = re.compile(r"\{.*\}", re.DOTALL)


@runtime_checkable
class LLMClient(Protocol):
    def complete(self, system: str, prompt: str) -> str: ...


def parse_json_response(text: str) -> dict[str, object]:
    """Extract and parse the first JSON object from a model response.

    Tolerates code fences and surrounding prose. Raises ``ValueError`` if no
    valid JSON object is present.
    """
    match = _JSON_BLOCK.search(text)
    if not match:
        raise ValueError("No JSON object found in model response")
    try:
        result = json.loads(match.group(0))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Malformed JSON in model response: {exc}") from exc
    if not isinstance(result, dict):
        raise ValueError("Model response JSON was not an object")
    return result


class AnthropicClient:  # pragma: no cover - requires network + SDK
    def __init__(self, api_key: str, model: str) -> None:
        import anthropic

        self._client = anthropic.Anthropic(api_key=api_key)
        self._model = model

    def complete(self, system: str, prompt: str) -> str:
        message = self._client.messages.create(
            model=self._model,
            max_tokens=1024,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(block.text for block in message.content if block.type == "text")


class OpenAIClient:  # pragma: no cover - requires network + SDK
    def __init__(self, api_key: str, model: str) -> None:
        import openai

        self._client = openai.OpenAI(api_key=api_key)
        self._model = model

    def complete(self, system: str, prompt: str) -> str:
        resp = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
        )
        return resp.choices[0].message.content or ""


def get_llm_client(settings: Settings) -> LLMClient | None:
    """Build the configured LLM client, or ``None`` if unavailable.

    Returns ``None`` (rather than raising) when the API key is missing or the
    provider SDK is not installed, so callers can degrade gracefully.
    """
    try:
        if settings.llm_provider == "anthropic" and settings.anthropic_api_key:
            return AnthropicClient(settings.anthropic_api_key, settings.anthropic_model)
        if settings.llm_provider == "openai" and settings.openai_api_key:
            return OpenAIClient(settings.openai_api_key, settings.openai_model)
    except ImportError:  # pragma: no cover - SDK not installed
        return None
    return None
