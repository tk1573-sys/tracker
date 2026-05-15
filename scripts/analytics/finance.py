"""Finance analytics functions."""
from __future__ import annotations

import pandas as pd


def compute_kpis(transactions: pd.DataFrame, budget: pd.DataFrame) -> dict:
    """Compute top-level financial KPIs.

    Args:
        transactions: Transactions DataFrame.
        budget: Budget DataFrame.

    Returns:
        Dict with total_income, total_expense, budget_total,
        budget_remaining, net, savings_rate.
    """
    tx = transactions.copy()
    tx["_type"] = tx["Type"].astype(str).str.lower()

    total_income = float(tx[tx["_type"] == "income"]["Amount"].sum())
    total_expense = float(tx[tx["_type"] == "expense"]["Amount"].sum())
    budget_total = float(budget["MonthlyBudget"].sum())
    budget_remaining = budget_total - total_expense
    net = total_income - total_expense
    savings_rate = (net / total_income * 100) if total_income > 0 else 0.0

    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "budget_total": budget_total,
        "budget_remaining": budget_remaining,
        "net": net,
        "savings_rate": round(savings_rate, 2),
    }


def monthly_summary(transactions: pd.DataFrame) -> pd.DataFrame:
    """Aggregate income and expenses by month.

    Args:
        transactions: Transactions DataFrame with Date column.

    Returns:
        DataFrame with columns: Month, Income, Expense, Net.
    """
    tx = transactions.copy()
    tx["_type"] = tx["Type"].astype(str).str.lower()
    tx["Month"] = tx["Date"].dt.to_period("M").astype(str)

    income = tx[tx["_type"] == "income"].groupby("Month")["Amount"].sum().rename("Income")
    expense = tx[tx["_type"] == "expense"].groupby("Month")["Amount"].sum().rename("Expense")

    df = pd.concat([income, expense], axis=1).fillna(0).reset_index()
    df["Net"] = df["Income"] - df["Expense"]
    return df


def category_spend(transactions: pd.DataFrame) -> pd.DataFrame:
    """Expense breakdown by category.

    Args:
        transactions: Transactions DataFrame.

    Returns:
        DataFrame with columns: Category, Amount, Pct.
    """
    tx = transactions.copy()
    tx["_type"] = tx["Type"].astype(str).str.lower()
    df = (
        tx[tx["_type"] == "expense"]
        .groupby("Category")["Amount"]
        .sum()
        .reset_index()
        .sort_values("Amount", ascending=False)
    )
    total = df["Amount"].sum()
    df["Pct"] = (df["Amount"] / total * 100).round(1) if total > 0 else 0.0
    return df
