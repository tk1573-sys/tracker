"""AI-ready analytics insights module.

This module provides a clean interface for future LLM/AI integration.
Drop in an OpenAI, Anthropic, or local-LLM call wherever indicated by
the TODO comments to unlock AI-generated narratives and recommendations.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

import pandas as pd

from scripts.utilities.logger import get_logger

logger = get_logger(__name__)


class InsightsEngine:
    """Generates structured analytics insights ready for AI augmentation.

    Args:
        data: Dictionary of DataFrames keyed by dataset name.
        llm_client: Optional LLM client (e.g. openai.OpenAI instance).
            If None, AI narrative features are skipped and rule-based
            summaries are returned instead.
    """

    def __init__(
        self,
        data: Dict[str, pd.DataFrame],
        llm_client: Optional[Any] = None,
    ) -> None:
        self.data = data
        self.llm = llm_client

    def spending_summary(self) -> str:
        """Return a rule-based spending summary string.

        Returns:
            Human-readable spending summary.
        """
        from scripts.analytics.finance import compute_kpis, category_spend

        tx = self.data.get("transactions", pd.DataFrame())
        budget = self.data.get("budget", pd.DataFrame())
        if tx.empty:
            return "No transaction data available."

        kpis = compute_kpis(tx, budget)
        cat = category_spend(tx)
        top_cat = cat.iloc[0]["Category"] if not cat.empty else "N/A"

        summary = (
            f"Total income: {kpis['total_income']:,.2f}. "
            f"Total expenses: {kpis['total_expense']:,.2f}. "
            f"Net savings: {kpis['net']:,.2f} ({kpis['savings_rate']:.1f}% savings rate). "
            f"Highest spend category: {top_cat}."
        )

        if self.llm is not None:
            # TODO: Replace with real LLM call
            pass  # pragma: no cover

        return summary

    def habit_summary(self) -> str:
        """Return a rule-based habit completion summary.

        Returns:
            Human-readable habit summary.
        """
        from scripts.analytics.habits import completion_rate

        habits = self.data.get("habits", pd.DataFrame())
        if habits.empty:
            return "No habit data available."

        stats = completion_rate(habits)
        best = stats.loc[stats["Completion_Pct"].idxmax(), "Habit"] if not stats.empty else "N/A"
        worst = stats.loc[stats["Completion_Pct"].idxmin(), "Habit"] if not stats.empty else "N/A"
        avg = stats["Completion_Pct"].mean()

        return (
            f"Overall habit completion: {avg:.1f}%. "
            f"Best habit: {best}. "
            f"Needs improvement: {worst}."
        )

    def journal_sentiment(self) -> str:
        """Return mood trend analysis from journal data.

        Returns:
            Human-readable mood/sentiment summary.
        """
        journal = self.data.get("journal", pd.DataFrame())
        if journal.empty or "Mood" not in journal.columns:
            return "No journal mood data available."

        avg_mood = journal["Mood"].mean()
        trend = "improving" if journal["Mood"].iloc[-1] >= journal["Mood"].iloc[0] else "declining"

        return (
            f"Average mood score: {avg_mood:.1f}/5. "
            f"Mood trend: {trend}."
            # TODO: Pass journal entries to LLM for sentiment analysis
        )
