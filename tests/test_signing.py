"""Tests for content hashing / signing (.spec §9)."""

from __future__ import annotations

from healthcare_ai_governance.shared.signing import (
    canonical_json,
    content_hash,
    short_hash,
)


def test_hash_is_stable(sample_model_card) -> None:
    assert content_hash(sample_model_card) == content_hash(sample_model_card)


def test_hash_changes_on_modification(sample_model_card) -> None:
    before = content_hash(sample_model_card)
    modified = sample_model_card.model_copy(update={"version": "9.9"})
    assert content_hash(modified) != before


def test_canonical_json_key_order_independent() -> None:
    a = {"b": 1, "a": 2}
    b = {"a": 2, "b": 1}
    assert canonical_json(a) == canonical_json(b)
    assert content_hash(a) == content_hash(b)


def test_short_hash_is_prefix(sample_model_card) -> None:
    full = content_hash(sample_model_card)
    assert full.startswith(short_hash(sample_model_card))
    assert len(short_hash(sample_model_card, length=8)) == 8
