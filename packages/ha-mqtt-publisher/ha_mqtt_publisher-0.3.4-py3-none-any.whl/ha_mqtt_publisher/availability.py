"""Generic availability + signal helpers for MQTT services.

Lightweight utilities to publish simple online/offline presence to a chosen
MQTT topic (retained), and to integrate graceful shutdown via signals.

No Home Assistant dependency.
"""

from __future__ import annotations

from collections.abc import Callable
from contextlib import AbstractContextManager
import logging
import signal
from types import FrameType

logger = logging.getLogger(__name__)


class AvailabilityPublisher:
    """Publishes simple online/offline retained states to a topic.

    Expects a client with a ``publish(topic, payload, qos=0, retain=False)`` method
    (e.g., paho-mqtt client or library MQTTPublisher).
    """

    def __init__(self, mqtt_client, topic: str, qos: int = 0):
        self._client = mqtt_client
        self.topic = topic
        self.qos = qos

    def online(self, retain: bool = True) -> None:
        """Publish online state.

        Method name matches existing project to allow drop-in replacement.
        """
        try:
            self._client.publish(self.topic, "online", qos=self.qos, retain=retain)
        except Exception as e:  # pragma: no cover - defensive
            logger.warning("availability online failed: %s", e)

    def offline(self, retain: bool = True) -> None:
        """Publish offline state."""
        try:
            self._client.publish(self.topic, "offline", qos=self.qos, retain=retain)
        except Exception as e:  # pragma: no cover - defensive
            logger.warning("availability offline failed: %s", e)


class _SignalController(AbstractContextManager):
    def __init__(self, shutdown_cb: Callable[[], None]):
        self._shutdown_cb = shutdown_cb
        self._orig_int = None
        self._orig_term = None

    def __enter__(self):
        def _handler(
            signum: int, frame: FrameType | None
        ):  # pragma: no cover - OS signals
            try:
                self._shutdown_cb()
            finally:
                # Restore original then re-raise default behavior
                self.__exit__(None, None, None)

        self._orig_int = signal.getsignal(signal.SIGINT)
        self._orig_term = signal.getsignal(signal.SIGTERM)
        signal.signal(signal.SIGINT, _handler)
        signal.signal(signal.SIGTERM, _handler)
        return self

    def __exit__(self, exc_type, exc, tb):  # pragma: no cover - OS signals
        if self._orig_int is not None:
            signal.signal(signal.SIGINT, self._orig_int)
        if self._orig_term is not None:
            signal.signal(signal.SIGTERM, self._orig_term)
        return False


def install_signal_handlers(shutdown_cb: Callable[[], None]) -> _SignalController:
    """Context manager that installs SIGINT/SIGTERM handlers to call shutdown_cb."""
    return _SignalController(shutdown_cb)
