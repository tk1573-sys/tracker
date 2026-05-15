"""Habit analytics functions."""
from __future__ import annotations

import pandas as pd


def completion_rate(habits: pd.DataFrame) -> pd.DataFrame:
    """Habit completion rate per habit.

    Args:
        habits: Habits DataFrame with columns Date, Habit, Done.

    Returns:
        DataFrame with columns: Habit, Total, Done, Completion_Pct.
    """
    df = habits.copy()
    df["_done"] = df["Done"].astype(str).str.lower().isin(["yes", "true", "1"])

    summary = df.groupby("Habit").agg(
        Total=("_done", "count"),
        Done=("_done", "sum"),
    ).reset_index()
    summary["Completion_Pct"] = (summary["Done"] / summary["Total"] * 100).round(1)
    return summary


def streak(habits: pd.DataFrame, habit_name: str) -> int:
    """Current consecutive-day streak for a specific habit.

    Args:
        habits: Habits DataFrame.
        habit_name: Name of the habit.

    Returns:
        Current streak length in days.
    """
    df = habits[habits["Habit"] == habit_name].copy()
    df["_done"] = df["Done"].astype(str).str.lower().isin(["yes", "true", "1"])
    df = df.sort_values("Date", ascending=False)

    count = 0
    for done in df["_done"]:
        if done:
            count += 1
        else:
            break
    return count


def weekly_summary(habits: pd.DataFrame) -> pd.DataFrame:
    """Weekly habit completion summary.

    Args:
        habits: Habits DataFrame.

    Returns:
        DataFrame with Week, Habit, Completion_Pct columns.
    """
    df = habits.copy()
    df["_done"] = df["Done"].astype(str).str.lower().isin(["yes", "true", "1"])
    df["Week"] = df["Date"].dt.to_period("W").astype(str)

    total = df.groupby(["Week", "Habit"])["_done"].count().rename("Total")
    done = df.groupby(["Week", "Habit"])["_done"].sum().rename("Done")
    summary = pd.concat([total, done], axis=1).reset_index()
    summary["Completion_Pct"] = (summary["Done"] / summary["Total"] * 100).round(1)
    return summary
