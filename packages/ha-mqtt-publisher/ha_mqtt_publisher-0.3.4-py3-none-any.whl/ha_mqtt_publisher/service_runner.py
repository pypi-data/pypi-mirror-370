"""Service runner conveniences for MQTT-backed services.

Provides simple helpers to run a one-shot cycle or a periodic loop with
optional availability publishing and graceful signal handling.
"""

from __future__ import annotations

from collections.abc import Callable
import signal
import threading
import time

from .availability import AvailabilityPublisher


def run_service_once(
    *,
    setup: Callable[[], None] | None = None,
    cycle: Callable[[], None] | None = None,
    teardown: Callable[[], None] | None = None,
    availability: AvailabilityPublisher | None = None,
) -> None:
    """Run a single service cycle with optional availability and hooks.

    - Calls setup() once (if provided)
    - Marks availability online
    - Calls cycle() once (if provided)
    - Marks availability offline
    - Calls teardown() (if provided)
    """

    if setup:
        setup()

    if availability:
        availability.online()

    try:
        if cycle:
            cycle()
    finally:
        if availability:
            availability.offline()
        if teardown:
            teardown()


def run_service_loop(
    *,
    interval_s: float,
    on_tick: Callable[[], None],
    availability: AvailabilityPublisher | None = None,
    stop_event: threading.Event | None = None,
    install_signals: bool = True,
) -> None:
    """Run a periodic loop calling on_tick every interval_s seconds.

    - Optionally publishes availability online/offline
    - Supports graceful shutdown via signals (SIGINT/SIGTERM) or provided stop_event
    """

    local_event: threading.Event | None = None

    if stop_event is None:
        local_event = threading.Event()
        stop_event = local_event

    # Install signal handlers to trigger stop
    cleanup: list[Callable[[], None]] = []
    if install_signals:

        def _stop_handler(signum, frame):  # pragma: no cover - tiny glue
            try:
                stop_event.set()
            except Exception:
                pass

        previous_int = signal.getsignal(signal.SIGINT)
        previous_term = signal.getsignal(signal.SIGTERM)
        signal.signal(signal.SIGINT, _stop_handler)
        signal.signal(signal.SIGTERM, _stop_handler)

        def _restore():
            try:
                signal.signal(signal.SIGINT, previous_int)
                signal.signal(signal.SIGTERM, previous_term)
            except Exception:
                pass

        cleanup.append(_restore)

    # Availability online
    if availability:
        availability.online()

    try:
        # Main loop
        while not stop_event.is_set():
            start = time.time()
            on_tick()
            # Sleep remaining time, if any
            elapsed = time.time() - start
            remaining = interval_s - elapsed
            if remaining > 0:
                stop_event.wait(remaining)
    finally:
        if availability:
            availability.offline()
        for fn in cleanup:
            try:
                fn()
            except Exception:
                pass
