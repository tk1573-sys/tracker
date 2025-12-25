# New Year Daily Tracker — Excel + Power BI Guide

Overview
- Purpose: Track budget (income/expenses), daily habits, New Year resolutions progress, expenses breakdown, and a daily journal.
- Files included (CSV): `tracker_transactions.csv`, `tracker_habits.csv`, `tracker_resolutions.csv`, `tracker_budget.csv`, `tracker_journal.csv`.
- Use: Run the provided generator script to produce a fully styled Excel workbook (tracker_dashboard.xlsx). Follow Power BI instructions in the `powerbi/` folder to build the .pbix report locally.

Quick start
1. Clone the repository locally or download the ZIP from GitHub.
2. Install Python 3.8+ and required packages: `pip install pandas openpyxl xlsxwriter`
3. Run: `python generate_tracker_workbook.py` — this will read the CSV files and create `tracker_dashboard.xlsx` in the repository root.
4. Open Power BI Desktop and follow the `powerbi/visuals_instructions.md` and apply `powerbi/theme.json` to build the full `tracker_report.pbix`.

Files included
- CSV seeds: transactions, habits, resolutions, budget, journal
- `generate_tracker_workbook.py`: Python generator that creates `tracker_dashboard.xlsx` from the CSVs
- `powerbi/` folder: theme JSON, DAX measures, and step-by-step visuals instructions
