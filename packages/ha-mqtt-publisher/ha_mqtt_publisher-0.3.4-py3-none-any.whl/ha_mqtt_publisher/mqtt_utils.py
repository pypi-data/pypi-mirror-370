"""MQTT callback normalization helpers for ha_mqtt_publisher.

These helpers are intentionally lightweight and pure (do not mutate os.environ)
so they are safe for library use.
"""

from typing import Any


def extract_reason_code(*args: tuple[Any, ...], **kwargs: dict) -> Any | None:
    """Extract a likely reason_code from positional args or kwargs.

    Best-effort rules:
    - Search positional args from right-to-left for an int-like value.
    - Fall back to kwargs 'reason_code' or 'rc' if present.
    - Return None if nothing found.
    """
    for a in reversed(args):
        if isinstance(a, int) and not isinstance(a, bool):
            return a
        if hasattr(a, "__int__"):
            try:
                return int(a)
            except Exception:
                pass

    for key in ("reason_code", "rc"):
        if key in kwargs and kwargs[key] is not None:
            return kwargs[key]

    return None


def extract_properties(*args: tuple[Any, ...], **kwargs: dict) -> Any | None:
    """Extract MQTT v5 properties object from args/kwargs if present.

    Prefer explicit kw 'properties', else take the last positional arg that
    doesn't look like an int-like reason code.
    """
    if "properties" in kwargs and kwargs["properties"] is not None:
        return kwargs["properties"]

    if args:
        last = args[-1]
        if not (isinstance(last, int) or hasattr(last, "__int__")):
            return last
        if len(args) >= 2:
            cand = args[-2]
            if not (isinstance(cand, int) or hasattr(cand, "__int__")):
                return cand

    return None


def safe_on_connect(func):
    """Decorator to normalize on_connect callbacks to (client, userdata, reason_code, properties).

    Usage:
        @safe_on_connect
        def on_connect(client, userdata, reason_code, properties):
            ...
    """

    def wrapper(client, userdata, *args, **kwargs):
        reason_code = extract_reason_code(*args, **kwargs)
        properties = extract_properties(*args, **kwargs)
        return func(client, userdata, reason_code, properties)

    return wrapper


def safe_on_disconnect(func):
    """Decorator to normalize on_disconnect callbacks to (client, userdata, reason_code, properties).

    Works for both v1 signature (client, userdata, rc) and v2 (client, userdata, reason_code, properties).
    """

    def wrapper(client, userdata, *args, **kwargs):
        reason_code = extract_reason_code(*args, **kwargs)
        properties = extract_properties(*args, **kwargs)
        return func(client, userdata, reason_code, properties)

    return wrapper


def safe_on_publish(func):
    """Decorator to normalize on_publish callbacks to (client, userdata, mid, reason_codes, properties).

    Supports v1 (client, userdata, mid) and v2 (client, userdata, mid, reason_codes, properties).
    """

    def wrapper(client, userdata, *args, **kwargs):
        # mid is generally the first positional arg
        mid = None
        reason_codes = None
        properties = None
        if args:
            mid = args[0]
            # Look for reason_codes/properties after mid
            if len(args) >= 3:
                # case: (mid, reason_codes, properties)
                reason_codes = args[1]
                properties = args[2]
            elif len(args) == 2:
                # ambiguous: second arg might be reason_codes or properties; try to heuristically pick
                cand = args[1]
                if hasattr(cand, "__int__") or isinstance(cand, int):
                    reason_codes = cand
                else:
                    properties = cand

        # allow kwargs overrides
        if "mid" in kwargs:
            mid = kwargs.get("mid")
        if "reason_codes" in kwargs:
            reason_codes = kwargs.get("reason_codes")
        if "properties" in kwargs:
            properties = kwargs.get("properties")

        return func(client, userdata, mid, reason_codes, properties)

    return wrapper
