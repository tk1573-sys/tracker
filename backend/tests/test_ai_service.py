import unittest
from datetime import UTC, datetime, timedelta

from app.services.ai import RuleBasedAIProvider


class RuleBasedAIProviderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.provider = RuleBasedAIProvider()
        self.now = datetime(2026, 5, 20, 10, 0, tzinfo=UTC)

    def test_parses_relative_reminder_command(self) -> None:
        parsed = self.provider.parse("remind me in 45 minutes to review sprint board", self.now)

        self.assertEqual(parsed.intent, "create_task_with_reminder")
        self.assertFalse(parsed.needs_clarification)
        self.assertEqual(parsed.title, "review sprint board")
        self.assertEqual(parsed.remind_at, self.now + timedelta(minutes=45))

    def test_requests_clarification_for_past_day_time(self) -> None:
        parsed = self.provider.parse("remind me today at 8am to stretch", self.now)

        self.assertTrue(parsed.needs_clarification)
        self.assertEqual(parsed.intent, "create_task_with_reminder")
        self.assertIsNone(parsed.remind_at)
