"""Unit tests for finance analytics module."""
import pytest
import pandas as pd
from scripts.analytics.finance import compute_kpis, monthly_summary, category_spend


@pytest.fixture
def sample_transactions():
    return pd.DataFrame({
        "Date": pd.to_datetime(["2025-01-01", "2025-01-05", "2025-01-10", "2025-02-01"]),
        "Category": ["Income", "Groceries", "Transport", "Income"],
        "Amount": [3000.0, 100.0, 50.0, 2000.0],
        "Type": ["Income", "Expense", "Expense", "Income"],
    })


@pytest.fixture
def sample_budget():
    return pd.DataFrame({
        "Category": ["Groceries", "Transport"],
        "MonthlyBudget": [400.0, 100.0],
    })


def test_compute_kpis_total_income(sample_transactions, sample_budget):
    kpis = compute_kpis(sample_transactions, sample_budget)
    assert kpis["total_income"] == pytest.approx(5000.0)


def test_compute_kpis_total_expense(sample_transactions, sample_budget):
    kpis = compute_kpis(sample_transactions, sample_budget)
    assert kpis["total_expense"] == pytest.approx(150.0)


def test_compute_kpis_net(sample_transactions, sample_budget):
    kpis = compute_kpis(sample_transactions, sample_budget)
    assert kpis["net"] == pytest.approx(4850.0)


def test_savings_rate(sample_transactions, sample_budget):
    kpis = compute_kpis(sample_transactions, sample_budget)
    assert kpis["savings_rate"] == pytest.approx(97.0)


def test_monthly_summary_columns(sample_transactions):
    df = monthly_summary(sample_transactions)
    assert "Month" in df.columns
    assert "Income" in df.columns
    assert "Expense" in df.columns
    assert "Net" in df.columns


def test_category_spend_sorted(sample_transactions):
    cat = category_spend(sample_transactions)
    amounts = cat["Amount"].tolist()
    assert amounts == sorted(amounts, reverse=True)
