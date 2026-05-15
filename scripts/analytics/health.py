"""Health analytics functions."""
from __future__ import annotations

import pandas as pd


def compute_bmi(weight_kg: float, height_cm: float) -> float:
    """Calculate BMI.

    Args:
        weight_kg: Weight in kilograms.
        height_cm: Height in centimetres.

    Returns:
        BMI rounded to 1 decimal place.
    """
    if height_cm <= 0:
        return 0.0
    height_m = height_cm / 100
    return round(weight_kg / (height_m ** 2), 1)


def bmi_category(bmi: float) -> str:
    """Return WHO BMI category label."""
    if bmi < 18.5:
        return "Underweight"
    if bmi < 25.0:
        return "Normal"
    if bmi < 30.0:
        return "Overweight"
    return "Obese"


def weekly_averages(health: pd.DataFrame) -> pd.DataFrame:
    """Weekly averages of health metrics.

    Args:
        health: Health DataFrame.

    Returns:
        DataFrame with Week and average columns for numeric metrics.
    """
    df = health.copy()
    df["Week"] = df["Date"].dt.to_period("W").astype(str)
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    return df.groupby("Week")[numeric_cols].mean().round(2).reset_index()
