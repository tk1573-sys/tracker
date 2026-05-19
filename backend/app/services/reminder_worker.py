from __future__ import annotations

import threading
import time
from datetime import UTC, datetime

from app.core.config import settings
from app.core.logging import get_logger
from app.db.session import SessionLocal
from app.services.common import run_with_retry
from app.services.reminders import process_due_reminders, process_follow_ups

logger = get_logger(__name__)


class ReminderWorker:
    def __init__(
        self,
        interval_seconds: int = 60,
        retry_attempts: int = 3,
        retry_backoff_seconds: float = 0.25,
    ) -> None:
        self.interval_seconds = interval_seconds
        self.retry_attempts = retry_attempts
        self.retry_backoff_seconds = retry_backoff_seconds
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
        logger.info("Reminder worker stopped")

    def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                sent, follow = run_with_retry(
                    self._process_cycle,
                    max_attempts=self.retry_attempts,
                    backoff_seconds=self.retry_backoff_seconds,
                )
                if sent or follow:
                    logger.info("Reminder worker processed: sent=%s follow_ups=%s", sent, follow)
            except Exception as exc:  # pragma: no cover
                logger.exception("Reminder worker cycle failed: %s", exc)
            self._stop_event.wait(self.interval_seconds)

    def _process_cycle(self) -> tuple[int, int]:
        now = datetime.now(UTC)
        with SessionLocal() as db:
            sent = process_due_reminders(db, now=now)
            follow = process_follow_ups(db, now=now)
            return sent, follow


worker = ReminderWorker(
    interval_seconds=settings.reminder_worker_interval_seconds,
    retry_attempts=settings.reminder_worker_retry_attempts,
    retry_backoff_seconds=settings.reminder_worker_retry_backoff_seconds,
)
