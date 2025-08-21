"""
Idempotency utilities.

Provides helpers to generate idempotency keys and maintain a simple
deduplication policy to avoid re-sending the same payload to target
endpoints during retries or replays.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Set, Tuple


def generate_idempotency_key(payload: Any, *, salt: str = "") -> str:
    """Generate a stable idempotency key from a JSON-serializable payload."""
    try:
        data = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    except Exception:
        data = str(payload)
    return hashlib.sha256((salt + "|" + data).encode("utf-8")).hexdigest()


class InMemoryDeduplicator:
    """Simple in-memory deduplication set keyed by endpoint + idempotency key."""

    def __init__(self) -> None:
        self._seen: Set[Tuple[str, str]] = set()

    def has_seen(self, endpoint: str, idem_key: str) -> bool:
        return (endpoint, idem_key) in self._seen

    def mark_seen(self, endpoint: str, idem_key: str) -> None:
        self._seen.add((endpoint, idem_key))
