from contextlib import nullcontext
import unittest

from app.services.reminder_worker import ReminderWorker


class ReminderWorkerTests(unittest.TestCase):
    def test_retries_failed_cycle_before_waiting_for_next_interval(self) -> None:
        attempts = {"due": 0}
        worker: ReminderWorker | None = None

        def due_processor(_: object, *, now=None) -> int:
            attempts["due"] += 1
            if attempts["due"] == 1:
                raise RuntimeError("transient failure")
            return 1

        def follow_up_processor(_: object, *, now=None) -> int:
            assert worker is not None
            worker._stop_event.set()
            return 1

        worker = ReminderWorker(
            interval_seconds=0.01,
            max_retry_attempts=1,
            retry_backoff_seconds=0.01,
            session_factory=lambda: nullcontext(object()),
            due_processor=due_processor,
            follow_up_processor=follow_up_processor,
        )

        worker.start()
        assert worker._thread is not None
        worker._thread.join(timeout=1)

        self.assertEqual(attempts["due"], 2)
        self.assertFalse(worker._thread.is_alive())
