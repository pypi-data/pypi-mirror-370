"""JSON publishing helpers for MQTT (generic).

Provides thin helpers to consistently publish retained JSON payloads with
optional timestamp injection and debug logging.
"""

from __future__ import annotations

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


def publish_json(
    client,
    topic: str,
    obj: dict[str, Any] | list[Any],
    *,
    qos: int = 0,
    retain: bool = True,
    ensure_ts_field: str | None = None,
    ts_value: str | None = None,
    debug: bool = False,
) -> None:
    """Publish an object as JSON.

    - client: has publish(topic, payload, qos, retain)
    - ensure_ts_field: if provided and obj is a dict, inject ts_value under this key when missing
    - ts_value: precomputed timestamp string; if None and ensure_ts_field set, a UTC ISO timestamp is generated
    """
    payload_obj = obj
    if (
        ensure_ts_field
        and isinstance(payload_obj, dict)
        and ensure_ts_field not in payload_obj
    ):
        payload_obj = dict(payload_obj)
        payload_obj[ensure_ts_field] = ts_value or _iso_now()
    if debug:
        logger.debug("publish_json topic=%s payload=%s", topic, payload_obj)
    client.publish(topic, json.dumps(payload_obj), qos=qos, retain=retain)


def publish_many(
    client,
    messages: list[tuple[str, dict[str, Any] | list[Any], int, bool]],
    *,
    debug: bool = False,
) -> None:
    """Publish many JSON messages.

    messages: list of (topic, obj, qos, retain)
    """
    for topic, obj, qos, retain in messages:
        publish_json(client, topic, obj, qos=qos, retain=retain, debug=debug)


def _iso_now() -> str:
    from datetime import UTC, datetime

    return datetime.now(UTC).isoformat()
