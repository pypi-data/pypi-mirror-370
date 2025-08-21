"""Generic MQTT command processing utilities.

A reusable version of the CommandProcessor used in Twickenham Events, designed
to be broker- and domain-agnostic. Handles JSON/plain payloads, acks, results,
single-flight, cooldowns, and a lightweight registry for UI exposure.
"""

from __future__ import annotations

from collections import deque
from collections.abc import Callable
from dataclasses import dataclass, field
import json
import logging
import threading
import time
from typing import Any
import uuid

logger = logging.getLogger(__name__)

Executor = Callable[[dict[str, Any]], tuple[str, str, dict[str, Any]]]


@dataclass
class CommandProcessor:
    client: Any  # object with publish()
    ack_topic: str
    result_topic: str
    max_history: int = 128
    retain_ack: bool = False
    retain_result: bool = False
    qos: int = 1
    executors: dict[str, Executor] = field(default_factory=dict)
    _registry_meta: dict[str, dict[str, Any]] = field(default_factory=dict)
    _last_success_ts: dict[str, float] = field(default_factory=dict)
    _auto_registry_topic: str | None = None
    _recent_ids: deque[str] = field(default_factory=deque, repr=False)
    _recent_set: set[str] = field(default_factory=set, repr=False)
    _seq: int = 0
    _active_lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    # Registration -------------------------------------------------------------
    def register(
        self,
        name: str,
        executor: Executor,
        *,
        description: str | None = None,
        args_schema: dict | None = None,
        outcome_codes: list[str] | None = None,
        qos_recommended: int | None = None,
        cooldown_seconds: int | None = None,
        requires_ai: bool | None = None,
    ) -> None:
        self.executors[name] = executor
        meta = {
            "name": name,
            "description": description or "",
            "args_schema": args_schema or {},
            "outcome_codes": outcome_codes
            or ["success", "validation_failed", "fatal_error", "busy"],
            "qos_recommended": qos_recommended
            if qos_recommended is not None
            else self.qos,
        }
        if cooldown_seconds is not None:
            meta["cooldown_seconds"] = cooldown_seconds
        if requires_ai is not None:
            meta["requires_ai"] = requires_ai
        self._registry_meta[name] = meta
        if self._auto_registry_topic:
            try:  # pragma: no cover - network safety
                self.publish_registry(self._auto_registry_topic)
            except Exception:  # pragma: no cover
                logger.debug("auto registry publish failed", exc_info=True)

    def enable_auto_registry_publish(self, topic: str) -> None:
        self._auto_registry_topic = topic

    # Public API ---------------------------------------------------------------
    def handle_raw(self, payload: bytes | str) -> None:
        if isinstance(payload, bytes):
            text = payload.decode("utf-8", errors="ignore")
        else:
            text = str(payload)
        stripped = text.strip()
        if not stripped:
            logger.warning("empty command payload ignored")
            return
        if stripped.startswith("{"):
            try:
                data = json.loads(stripped) or {}
            except Exception:
                data = {"command": stripped}
        else:
            data = {"command": stripped}
        self._process(data)

    # Internal ----------------------------------------------------------------
    def _next_seq(self) -> int:
        self._seq += 1
        return self._seq

    def _publish(self, topic: str, payload: dict[str, Any], retain: bool) -> None:
        try:
            self.client.publish(topic, json.dumps(payload), qos=self.qos, retain=retain)
        except Exception as e:  # pragma: no cover
            logger.error("command publish failed topic=%s error=%s", topic, e)

    def _process(self, data: dict[str, Any]) -> None:
        cmd = (data.get("command") or "").strip().lower()
        if not cmd:
            logger.warning("command with no name ignored")
            return
        cmd_id = (data.get("id") or "").strip() or str(uuid.uuid4())
        if cmd_id in self._recent_set:
            logger.info("duplicate command ignored id=%s command=%s", cmd_id, cmd)
            return
        self._recent_ids.append(cmd_id)
        self._recent_set.add(cmd_id)
        if len(self._recent_ids) > self.max_history:
            old = self._recent_ids.popleft()
            self._recent_set.discard(old)
        seq = self._next_seq()
        received_ts = self._iso_now()
        ack = {
            "id": cmd_id,
            "command": cmd,
            "received_ts": received_ts,
            "status": "received",
            "seq": seq,
        }
        self._publish(self.ack_topic, ack, retain=self.retain_ack)
        executor = self.executors.get(cmd)
        if not executor:
            result = {
                "id": cmd_id,
                "command": cmd,
                "completed_ts": self._iso_now(),
                "outcome": "unknown_command",
                "details": "No executor registered",
                "duration_ms": 0,
                "seq": self._next_seq(),
            }
            self._publish(self.result_topic, result, retain=self.retain_result)
            return
        # Cooldown enforcement
        meta = self._registry_meta.get(cmd, {})
        cd = meta.get("cooldown_seconds")
        now = time.time()
        if isinstance(cd, int) and cd > 0 and cmd in self._last_success_ts:
            elapsed = now - self._last_success_ts[cmd]
            if elapsed < cd:
                remaining = int(cd - elapsed)
                result = {
                    "id": cmd_id,
                    "command": cmd,
                    "completed_ts": self._iso_now(),
                    "outcome": "cooldown",
                    "details": f"cooldown_active retry_after_s={remaining}",
                    "retry_after_s": remaining,
                    "duration_ms": 0,
                    "seq": self._next_seq(),
                }
                self._publish(self.result_topic, result, retain=self.retain_result)
                return
        threading.Thread(
            target=self._run_executor,
            args=(cmd_id, cmd, executor, data, received_ts),
            daemon=True,
        ).start()

    def _run_executor(
        self,
        cmd_id: str,
        cmd: str,
        executor: Executor,
        data: dict[str, Any],
        received_ts: str,
    ) -> None:
        start = time.time()
        if not self._active_lock.acquire(blocking=False):
            result = {
                "id": cmd_id,
                "command": cmd,
                "completed_ts": self._iso_now(),
                "outcome": "busy",
                "details": "Another command is executing",
                "duration_ms": 0,
                "seq": self._next_seq(),
            }
            self._publish(self.result_topic, result, retain=self.retain_result)
            return
        try:
            ctx = {
                "id": cmd_id,
                "command": cmd,
                "requested_ts": data.get("requested_ts"),
                "args": data.get("args") or {},
                "raw": data,
                "received_ts": received_ts,
            }
            outcome, details, extra = executor(ctx)
        except Exception as e:  # pragma: no cover
            logger.exception("executor failure id=%s command=%s", cmd_id, cmd)
            outcome = "fatal_error"
            details = str(e)
            extra = {}
        finally:
            if self._active_lock.locked():
                self._active_lock.release()
        duration_ms = int((time.time() - start) * 1000)
        result = {
            "id": cmd_id,
            "command": cmd,
            "completed_ts": self._iso_now(),
            "outcome": outcome,
            "details": details,
            "duration_ms": duration_ms,
            "seq": self._next_seq(),
        }
        if extra:
            result.update(extra)
        self._publish(self.result_topic, result, retain=self.retain_result)
        if outcome == "success":
            self._last_success_ts[cmd] = start

    @staticmethod
    def _iso_now() -> str:
        from datetime import UTC, datetime

        return datetime.now(UTC).isoformat()

    # Registry ----------------------------------------------------------------
    def build_registry_payload(
        self, *, service_name: str = "service"
    ) -> dict[str, Any]:
        commands = []
        for name, meta in self._registry_meta.items():
            entry = dict(meta)
            if name in self._last_success_ts:
                entry["last_success_ts"] = int(self._last_success_ts[name])
            commands.append(entry)
        return {
            "service": service_name,
            "registry_version": 1,
            "generated_ts": self._iso_now(),
            "commands": commands,
        }

    def publish_registry(
        self, topic: str, *, retain: bool = True, service_name: str = "service"
    ) -> None:
        payload = self.build_registry_payload(service_name=service_name)
        self._publish(topic, payload, retain=retain)


__all__ = ["CommandProcessor", "Executor"]
