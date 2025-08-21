"""Validation utilities for retained topics and basic invariants."""

from __future__ import annotations

from collections.abc import Callable
import time
from typing import Any


def validate_retained(
    client,
    topics: list[str],
    *,
    timeout_s: float = 2.0,
    on_message: Callable[[str, bytes], None] | None = None,
) -> dict[str, Any]:
    """Subscribe and capture retained payloads for a list of topics.

    Returns a dict of topic->payload (raw bytes). Topics not seen within timeout
    will be absent from the result.
    """

    seen: dict[str, Any] = {}

    def _cb(_client, _userdata, msg):  # pragma: no cover - thin glue
        try:
            seen[msg.topic] = msg.payload
            if on_message:
                on_message(msg.topic, msg.payload)
        except Exception:
            pass

    # Subscribe
    for t in topics:
        try:
            client.subscribe(t, qos=0, callback=_cb)
        except Exception:
            # Best-effort
            pass

    deadline = time.time() + max(0.05, float(timeout_s))
    while time.time() < deadline and len(seen) < len(topics):
        time.sleep(0.05)

    # Unsubscribe
    for t in topics:
        try:
            if hasattr(client, "unsubscribe"):
                client.unsubscribe(t)
        except Exception:
            pass

    return seen
