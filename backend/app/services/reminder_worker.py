from __future__ import annotations

import threading
from collections.abc import Callable
from datetime import UTC, datetime

from app.core.logging import get_logger
from app.db.session import SessionLocal
from app.services.reminders import process_due_reminders, process_follow_ups

logger = get_logger(__name__)


class ReminderWorker:
    def __init__(
        self,
        interval_seconds: int = 60,
        *,
        max_retry_attempts: int = 3,
        retry_backoff_seconds: int = 5,
        session_factory: Callable[[], object] = SessionLocal,
        due_processor: Callable[..., int] = process_due_reminders,
        follow_up_processor: Callable[..., int] = process_follow_ups,
        now_provider: Callable[[], datetime] | None = None,
    ) -> None:
        self.interval_seconds = interval_seconds
        self.max_retry_attempts = max_retry_attempts
        self.retry_backoff_seconds = retry_backoff_seconds
        self._session_factory = session_factory
        self._due_processor = due_processor
        self._follow_up_processor = follow_up_processor
        self._now_provider = now_provider or (lambda: datetime.now(UTC))
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, name="reminder-worker", daemon=True)
        self._thread.start()
        logger.info("Reminder worker started (interval=%ss)", self.interval_seconds)

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)
        self._thread = None
        logger.info("Reminder worker stopped")

    def _run_cycle(self) -> tuple[int, int]:
        now = self._now_provider()
        with self._session_factory() as db:
            sent = self._due_processor(db, now=now)
            follow = self._follow_up_processor(db, now=now)
        return sent, follow

    def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            processed = False
            for attempt in range(self.max_retry_attempts + 1):
                try:
                    sent, follow = self._run_cycle()
                    if sent or follow:
                        logger.info(
                            "Reminder worker processed",
                            extra={"event": "reminder_worker_processed", "sent": sent, "follow_ups": follow},
                        )
                    processed = True
                    break
                except Exception as exc:  # pragma: no cover
                    if attempt >= self.max_retry_attempts:
                        logger.exception(
                            "Reminder worker cycle failed",
                            extra={
                                "event": "reminder_worker_cycle_failed",
                                "attempt": attempt + 1,
                                "error_type": type(exc).__name__,
                            },
                        )
                        break
                    delay = min(self.retry_backoff_seconds * (2**attempt), self.interval_seconds)
                    logger.warning(
                        "Reminder worker retry scheduled",
                        extra={
                            "event": "reminder_worker_retry_scheduled",
                            "attempt": attempt + 1,
                            "delay_seconds": delay,
                            "error_type": type(exc).__name__,
                        },
                    )
                    if self._stop_event.wait(delay):
                        return
            if not processed and self._stop_event.is_set():
                return
            self._stop_event.wait(self.interval_seconds)


worker = ReminderWorker()
