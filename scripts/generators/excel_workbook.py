"""Excel workbook generator — produces dashboards/excel/tracker_dashboard.xlsx."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, Optional

import pandas as pd
import xlsxwriter

from scripts.analytics.finance import category_spend, compute_kpis, monthly_summary
from scripts.analytics.habits import completion_rate
from scripts.utilities.config_loader import get_app_config, get_dashboard_config
from scripts.utilities.logger import get_logger

logger = get_logger(__name__)

_BASE = Path(__file__).resolve().parents[2]


class TrackerWorkbookGenerator:
    """Generates the multi-sheet Excel analytics workbook.

    Args:
        data: Dictionary of DataFrames keyed by dataset name.
        output_path: Destination .xlsx path. Defaults to config value.
    """

    DARK = {
        "bg_dark": "#0b1220",
        "bg_medium": "#0f1720",
        "accent1": "#00E5FF",
        "accent2": "#7C4DFF",
        "accent3": "#00E676",
        "accent4": "#FFEA00",
        "warning": "#FF7043",
        "text_light": "#e6eef8",
        "text_muted": "#cbd5e1",
        "white": "#ffffff",
    }

    def __init__(
        self,
        data: Dict[str, pd.DataFrame],
        output_path: Optional[Path] = None,
    ) -> None:
        self.data = data
        app_cfg = get_app_config()
        self.currency_symbol = app_cfg.get("app", {}).get("currency_symbol", "₹")
        if output_path is None:
            rel = app_cfg.get("output", {}).get("excel_file", "dashboards/excel/tracker_dashboard.xlsx")
            output_path = _BASE / rel
        output_path.parent.mkdir(parents=True, exist_ok=True)
        self.output_path = output_path
        self._wb: Optional[xlsxwriter.Workbook] = None
        self._fmt: Dict = {}

    def generate(self) -> Path:
        """Build and write the Excel workbook.

        Returns:
            Path to the generated workbook file.
        """
        logger.info("Generating Excel workbook → %s", self.output_path)
        self._wb = xlsxwriter.Workbook(str(self.output_path))
        self._init_formats()

        self._write_dashboard()
        self._write_transactions()
        self._write_budget()
        self._write_habits()
        self._write_health()
        self._write_food()
        self._write_resolutions()
        self._write_journal()
        self._write_analytics()
        self._write_monthly_summary()
        self._write_category_analysis()
        self._write_chart_data()

        self._wb.close()
        logger.info("Workbook saved: %s", self.output_path.name)
        return self.output_path

    def _init_formats(self) -> None:
        c = self.DARK
        wb = self._wb

        self._fmt = {
            "header": wb.add_format({
                "bold": True, "bg_color": c["bg_medium"],
                "font_color": c["text_muted"], "border": 1,
                "border_color": c["accent2"], "align": "center",
                "valign": "vcenter",
            }),
            "default": wb.add_format({
                "font_color": c["text_light"], "bg_color": c["bg_dark"],
            }),
            "currency": wb.add_format({
                "num_format": "#,##0.00",
                "font_color": c["text_light"], "bg_color": c["bg_dark"],
            }),
            "pct": wb.add_format({
                "num_format": "0.0%",
                "font_color": c["text_light"], "bg_color": c["bg_dark"],
            }),
            "title": wb.add_format({
                "bold": True, "font_size": 14,
                "font_color": c["white"], "bg_color": c["bg_dark"],
            }),
            "kpi_label": wb.add_format({
                "bold": True, "font_size": 11,
                "font_color": c["accent1"], "bg_color": c["bg_medium"],
                "border": 1, "border_color": c["accent1"],
                "align": "left", "valign": "vcenter",
            }),
            "kpi_value": wb.add_format({
                "bold": True, "font_size": 13,
                "num_format": "#,##0.00",
                "font_color": c["accent4"], "bg_color": c["bg_medium"],
                "border": 1, "border_color": c["accent1"],
                "align": "right", "valign": "vcenter",
            }),
            "kpi_pct": wb.add_format({
                "bold": True, "font_size": 13,
                "num_format": "0.0%",
                "font_color": c["accent3"], "bg_color": c["bg_medium"],
                "border": 1, "border_color": c["accent1"],
                "align": "right", "valign": "vcenter",
            }),
            "section": wb.add_format({
                "bold": True, "font_size": 12,
                "font_color": c["accent2"], "bg_color": c["bg_dark"],
                "bottom": 2, "bottom_color": c["accent2"],
            }),
            "positive": wb.add_format({
                "num_format": "#,##0.00",
                "font_color": c["accent3"], "bg_color": c["bg_dark"],
            }),
            "negative": wb.add_format({
                "num_format": "#,##0.00",
                "font_color": c["warning"], "bg_color": c["bg_dark"],
            }),
            "date": wb.add_format({
                "num_format": "yyyy-mm-dd",
                "font_color": c["text_muted"], "bg_color": c["bg_dark"],
            }),
            "integer": wb.add_format({
                "num_format": "#,##0",
                "font_color": c["text_light"], "bg_color": c["bg_dark"],
            }),
            "decimal": wb.add_format({
                "num_format": "0.0",
                "font_color": c["text_light"], "bg_color": c["bg_dark"],
            }),
        }

    def _write_df(
        self,
        ws,
        df: pd.DataFrame,
        startrow: int = 0,
        startcol: int = 0,
        currency_cols: Optional[list] = None,
        pct_cols: Optional[list] = None,
        int_cols: Optional[list] = None,
        decimal_cols: Optional[list] = None,
    ) -> None:
        """Write a DataFrame to a worksheet with styling."""
        currency_cols = [c.lower() for c in (currency_cols or [])]
        pct_cols = [c.lower() for c in (pct_cols or [])]
        int_cols = [c.lower() for c in (int_cols or [])]
        decimal_cols = [c.lower() for c in (decimal_cols or [])]

        for c_idx, col in enumerate(df.columns.tolist()):
            ws.write(startrow, startcol + c_idx, col, self._fmt["header"])
            ws.set_column(startcol + c_idx, startcol + c_idx, max(len(str(col)) + 4, 14))

        for r_idx, row in enumerate(df.values.tolist()):
            for c_idx, val in enumerate(row):
                col_name = df.columns[c_idx].lower()
                row_pos = startrow + 1 + r_idx
                col_pos = startcol + c_idx

                if val is None or (isinstance(val, float) and pd.isna(val)):
                    ws.write(row_pos, col_pos, "", self._fmt["default"])
                elif isinstance(val, pd.Timestamp):
                    ws.write(row_pos, col_pos, val.strftime("%Y-%m-%d"), self._fmt["date"])
                elif isinstance(val, (int, float)):
                    if col_name in currency_cols:
                        fmt = self._fmt["currency"]
                    elif col_name in pct_cols:
                        fmt = self._fmt["pct"]
                    elif col_name in int_cols:
                        fmt = self._fmt["integer"]
                    elif col_name in decimal_cols:
                        fmt = self._fmt["decimal"]
                    else:
                        fmt = self._fmt["default"]
                    ws.write(row_pos, col_pos, val, fmt)
                else:
                    ws.write(row_pos, col_pos, str(val) if val is not None else "", self._fmt["default"])

    def _add_ws(self, name: str, tab_color: Optional[str] = None):
        ws = self._wb.add_worksheet(name)
        if tab_color:
            ws.set_tab_color(tab_color)
        ws.hide_gridlines(2)
        return ws

    def _write_section_title(self, ws, row: int, col: int, text: str, width: int = 4) -> None:
        ws.merge_range(row, col, row, col + width - 1, text, self._fmt["section"])

    def _write_dashboard(self) -> None:
        c = self.DARK
        dash = self._add_ws("Dashboard", c["bg_dark"])
        dash.set_column("A:A", 28)
        dash.set_column("B:B", 20)
        dash.set_column("C:C", 4)
        dash.set_column("D:H", 18)

        tx = self.data["transactions"]
        budget = self.data["budget"]
        habits = self.data["habits"]
        health = self.data.get("health", pd.DataFrame())
        resolutions = self.data["resolutions"]

        kpis = compute_kpis(tx, budget)
        habit_stats = completion_rate(habits)
        overall_habit_pct = habit_stats["Completion_Pct"].mean() if not habit_stats.empty else 0
        res_pct = 0.0
        if not resolutions.empty and "CurrentValue" in resolutions.columns and "MetricTarget" in resolutions.columns:
            res_pct = (resolutions["CurrentValue"] / resolutions["MetricTarget"].replace(0, 1)).clip(0, 1).mean() * 100

        dash.merge_range("A1:H1", "Personal Analytics Platform — Dashboard", self._fmt["title"])
        dash.set_row(0, 30)

        kpi_data = [
            ("Total Income", kpis["total_income"], "currency"),
            ("Total Expenses", kpis["total_expense"], "currency"),
            ("Budget Total", kpis["budget_total"], "currency"),
            ("Budget Remaining", kpis["budget_remaining"], "currency"),
            ("Net Savings", kpis["net"], "currency"),
            ("Savings Rate", kpis["savings_rate"], "pct"),
            ("Habit Completion", round(overall_habit_pct, 1), "pct"),
            ("Resolution Progress", round(res_pct, 1), "pct"),
        ]

        dash.write("A3", "KEY PERFORMANCE INDICATORS", self._fmt["section"])

        for i, (label, value, kind) in enumerate(kpi_data):
            row = 4 + i
            dash.set_row(row, 22)
            dash.write(row, 0, label, self._fmt["kpi_label"])
            if kind == "currency":
                dash.write(row, 1, value, self._fmt["kpi_value"])
            else:
                dash.write(row, 1, value, self._fmt["kpi_pct"])

        if not health.empty:
            last = health.sort_values("Date").iloc[-1]
            dash.write("A13", "HEALTH SNAPSHOT", self._fmt["section"])
            health_kpis = [
                ("Latest Weight (kg)", last.get("Weight_kg", "N/A")),
                ("Latest Sleep (hrs)", last.get("Sleep_Hours", "N/A")),
                ("Latest Steps", last.get("Steps", "N/A")),
                ("Latest Water (L)", last.get("Water_Liters", "N/A")),
                ("Latest Mood", last.get("Mood_Score", "N/A")),
            ]
            for i, (label, value) in enumerate(health_kpis):
                row = 14 + i
                dash.set_row(row, 22)
                dash.write(row, 0, label, self._fmt["kpi_label"])
                dash.write(row, 1, value, self._fmt["decimal"])

    def _write_transactions(self) -> None:
        tx = self.data["transactions"]
        ws = self._add_ws("Transactions", "#00E5FF")
        ws.freeze_panes(1, 0)
        self._write_section_title(ws, 0, 0, "TRANSACTIONS LEDGER", 6)
        self._write_df(ws, tx, startrow=1, currency_cols=["Amount"])

    def _write_budget(self) -> None:
        budget = self.data["budget"]
        ws = self._add_ws("Budget", "#7C4DFF")
        ws.freeze_panes(1, 0)
        self._write_section_title(ws, 0, 0, "BUDGET PLANNER", 3)
        self._write_df(ws, budget, startrow=1, currency_cols=["MonthlyBudget"])

    def _write_habits(self) -> None:
        habits = self.data["habits"]
        ws = self._add_ws("Habits", "#00E676")
        ws.freeze_panes(1, 0)
        self._write_section_title(ws, 0, 0, "HABIT TRACKER", 4)
        self._write_df(ws, habits, startrow=1)

        stats = completion_rate(habits)
        start = len(habits) + 4
        ws.write(start, 0, "HABIT COMPLETION SUMMARY", self._fmt["section"])
        self._write_df(ws, stats, startrow=start + 1, pct_cols=["completion_pct"])

    def _write_health(self) -> None:
        health = self.data.get("health", pd.DataFrame())
        ws = self._add_ws("Health", "#FF7043")
        ws.freeze_panes(1, 0)
        self._write_section_title(ws, 0, 0, "HEALTH TRACKER", 10)
        if not health.empty:
            self._write_df(
                ws, health, startrow=1,
                decimal_cols=["weight_kg", "bmi", "sleep_hours", "water_liters"],
                int_cols=["steps", "calories_burned", "mood_score"],
            )

    def _write_food(self) -> None:
        food = self.data.get("food", pd.DataFrame())
        ws = self._add_ws("Food Tracker", "#FFEA00")
        ws.freeze_panes(1, 0)
        self._write_section_title(ws, 0, 0, "FOOD & NUTRITION TRACKER", 8)
        if not food.empty:
            self._write_df(
                ws, food, startrow=1,
                int_cols=["calories", "protein_g", "carbs_g", "fat_g"],
            )

    def _write_resolutions(self) -> None:
        res = self.data["resolutions"]
        ws = self._add_ws("Resolutions", "#29B6F6")
        ws.freeze_panes(1, 0)
        self._write_section_title(ws, 0, 0, "NEW YEAR RESOLUTIONS", 7)
        self._write_df(ws, res, startrow=1)

    def _write_journal(self) -> None:
        journal = self.data["journal"]
        ws = self._add_ws("Journal", "#7C4DFF")
        ws.freeze_panes(1, 0)
        ws.set_column("C:C", 60)
        self._write_section_title(ws, 0, 0, "DAILY JOURNAL", 4)
        self._write_df(ws, journal, startrow=1)

    def _write_analytics(self) -> None:
        tx = self.data["transactions"]
        budget = self.data["budget"]
        ws = self._add_ws("Analytics", "#00E5FF")

        kpis = compute_kpis(tx, budget)
        cat = category_spend(tx)

        ws.write("A1", "FINANCE ANALYTICS", self._fmt["section"])
        rows = [
            ("Total Income", kpis["total_income"], "currency"),
            ("Total Expenses", kpis["total_expense"], "currency"),
            ("Net Savings", kpis["net"], "currency"),
            ("Savings Rate (%)", kpis["savings_rate"], "decimal"),
            ("Budget Utilisation (%)", round(kpis["total_expense"] / kpis["budget_total"] * 100, 1) if kpis["budget_total"] else 0, "decimal"),
        ]
        for i, (lbl, val, kind) in enumerate(rows):
            ws.write(1 + i, 0, lbl, self._fmt["kpi_label"])
            fmt = self._fmt["kpi_value"] if kind == "currency" else self._fmt["decimal"]
            ws.write(1 + i, 1, val, fmt)

        ws.write("A8", "CATEGORY SPEND BREAKDOWN", self._fmt["section"])
        self._write_df(ws, cat, startrow=9, currency_cols=["amount"])

    def _write_monthly_summary(self) -> None:
        tx = self.data["transactions"]
        ws = self._add_ws("Monthly Summary", "#7C4DFF")
        ws.freeze_panes(1, 0)
        self._write_section_title(ws, 0, 0, "MONTHLY INCOME vs EXPENSE", 4)
        mon = monthly_summary(tx)
        self._write_df(ws, mon, startrow=1, currency_cols=["income", "expense", "net"])

        if len(mon) > 0:
            chart = self._wb.add_chart({"type": "column"})
            n = len(mon)
            chart.add_series({
                "name": "Income",
                "categories": f"='Monthly Summary'!$A$3:$A${2 + n}",
                "values": f"='Monthly Summary'!$B$3:$B${2 + n}",
                "fill": {"color": "#00E676"},
            })
            chart.add_series({
                "name": "Expense",
                "categories": f"='Monthly Summary'!$A$3:$A${2 + n}",
                "values": f"='Monthly Summary'!$C$3:$C${2 + n}",
                "fill": {"color": "#FF7043"},
            })
            chart.set_title({"name": "Monthly Income vs Expense"})
            chart.set_style(11)
            ws.insert_chart("F2", chart, {"x_offset": 10, "y_offset": 10})

    def _write_category_analysis(self) -> None:
        tx = self.data["transactions"]
        ws = self._add_ws("Category Analysis", "#00E676")
        ws.freeze_panes(1, 0)
        self._write_section_title(ws, 0, 0, "SPEND BY CATEGORY", 3)
        cat = category_spend(tx)
        self._write_df(ws, cat, startrow=1, currency_cols=["amount"])

        if len(cat) > 0:
            pie = self._wb.add_chart({"type": "pie"})
            n = len(cat)
            pie.add_series({
                "name": "Spend by Category",
                "categories": f"='Category Analysis'!$A$3:$A${2 + n}",
                "values": f"='Category Analysis'!$B$3:$B${2 + n}",
            })
            pie.set_title({"name": "Category Spend Distribution"})
            pie.set_style(10)
            ws.insert_chart("E2", pie, {"x_offset": 10, "y_offset": 10})

    def _write_chart_data(self) -> None:
        """Hidden sheet holding raw aggregated data for chart references."""
        ws = self._add_ws("_ChartData")
        ws.hide()
        tx = self.data["transactions"]
        cat = category_spend(tx)
        self._write_df(ws, cat, startrow=0, currency_cols=["amount"])
