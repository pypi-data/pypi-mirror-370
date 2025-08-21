"""Topic conventions helper.

Provides a tiny helper to derive common MQTT topics used by apps.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TopicMap:
    base: str

    @property
    def status(self) -> str:
        return f"{self.base}/status"

    @property
    def availability(self) -> str:
        return f"{self.base}/availability"

    @property
    def events(self) -> str:
        return f"{self.base}/events"

    @property
    def commands(self) -> str:
        return f"{self.base}/cmd"

    def cmd(self, name: str) -> str:
        return f"{self.commands}/{name}"
