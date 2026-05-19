from __future__ import annotations

import threading
import time
from datetime import UTC, datetime

from app.core.logging import get_logger
from app.db.session import SessionLocal
from app.services.reminders import process_due_reminders, process_follow_ups

logger = get_logger(__name__)


class ReminderWorker:
    def __init__(self, interval_seconds: int = 60) -> None:
        self.interval_seconds = interval_seconds
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
                with SessionLocal() as db:
                    sent = process_due_reminders(db, now=datetime.now(UTC))
                    follow = process_follow_ups(db, now=datetime.now(UTC))
                    if sent or follow:
                        logger.info("Reminder worker processed: sent=%s follow_ups=%s", sent, follow)
            except Exception as exc:  # pragma: no cover
                logger.exception("Reminder worker cycle failed: %s", exc)
            self._stop_event.wait(self.interval_seconds)


worker = ReminderWorker()
