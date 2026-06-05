"""Content hashing for tamper-evidence (.spec §6.3, §15.6).

The "signature" used throughout the toolkit is a SHA-256 content hash, **not** a
cryptographic signature. It detects whether a document's content changed after it
was generated; it does **not** authenticate the assessor or signer. This
limitation is stated plainly here and in each module that uses it (ADR-006 would
document a future move to ECDSA signing if organizations require authentication).
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from pydantic import BaseModel


def canonical_json(data: BaseModel | dict[str, Any]) -> str:
    """Serialize to canonical JSON: sorted keys, no insignificant whitespace.

    Two inputs with the same content always produce the same string, so the
    hash is stable across runs and machines.
    """
    payload = data.model_dump(mode="json") if isinstance(data, BaseModel) else data
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def content_hash(data: BaseModel | dict[str, Any]) -> str:
    """Return the hex SHA-256 of the canonical JSON of ``data``."""
    return hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest()


def short_hash(data: BaseModel | dict[str, Any], length: int = 12) -> str:
    """A truncated content hash for compact display (e.g. PDF footers)."""
    return content_hash(data)[:length]
