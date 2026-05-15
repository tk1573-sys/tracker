"""Unit tests for habits analytics module."""
import pytest
import pandas as pd
from scripts.analytics.habits import completion_rate, streak


@pytest.fixture
def sample_habits():
    return pd.DataFrame({
        "Date": pd.to_datetime([
            "2025-01-01", "2025-01-02", "2025-01-03",
            "2025-01-01", "2025-01-02",
        ]),
        "Habit": ["Exercise", "Exercise", "Exercise", "Read", "Read"],
        "Done": ["Yes", "No", "Yes", "Yes", "Yes"],
        "Notes": ["", "", "", "", ""],
    })


def test_completion_rate_columns(sample_habits):
    stats = completion_rate(sample_habits)
    assert set(["Habit", "Total", "Done", "Completion_Pct"]).issubset(set(stats.columns))


def test_completion_rate_exercise(sample_habits):
    stats = completion_rate(sample_habits)
    ex = stats[stats["Habit"] == "Exercise"].iloc[0]
    assert ex["Total"] == 3
    assert ex["Done"] == 2
    assert ex["Completion_Pct"] == pytest.approx(66.7, abs=0.1)


def test_streak_exercise(sample_habits):
    s = streak(sample_habits, "Exercise")
    assert s == 1


def test_streak_read(sample_habits):
    s = streak(sample_habits, "Read")
    assert s == 2
