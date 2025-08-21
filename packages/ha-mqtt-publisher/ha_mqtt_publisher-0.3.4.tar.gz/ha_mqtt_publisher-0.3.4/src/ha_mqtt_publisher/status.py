"""Status payload shaping helpers."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class StatusError:
    type: str
    message: str
    when: str | None = None
    extra: dict[str, Any] | None = None


@dataclass
class StatusPayload:
    status: str
    event_count: int = 0
    last_run_ts: int | None = None
    last_run_iso: str | None = None
    ai_enabled: bool | None = None
    ai_error_count: int = 0
    publish_error_count: int = 0
    error_count: int = 0
    errors: list[StatusError] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        d = asdict(self)
        # Convert nested dataclasses
        d["errors"] = [asdict(e) for e in self.errors]
        return d

    def mark_run(self) -> None:
        now = datetime.now(tz=UTC)
        self.last_run_ts = int(now.timestamp())
        self.last_run_iso = now.isoformat()

    def add_error(
        self, type: str, message: str, *, when_iso: str | None = None, **extra
    ) -> None:
        self.error_count += 1
        self.errors.append(
            StatusError(type=type, message=message, when=when_iso, extra=extra or None)
        )

    def cap_errors(self, max_items: int = 20) -> None:
        if len(self.errors) > max_items:
            self.errors = self.errors[-max_items:]
