"""Unit tests for health analytics module."""
import pytest
from scripts.analytics.health import compute_bmi, bmi_category


def test_bmi_normal():
    bmi = compute_bmi(70.0, 175.0)
    assert bmi == pytest.approx(22.9, abs=0.1)


def test_bmi_category_normal():
    assert bmi_category(22.9) == "Normal"


def test_bmi_category_overweight():
    assert bmi_category(27.0) == "Overweight"


def test_bmi_category_underweight():
    assert bmi_category(17.0) == "Underweight"


def test_bmi_zero_height():
    assert compute_bmi(70.0, 0.0) == 0.0
