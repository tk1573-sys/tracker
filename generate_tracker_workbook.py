"""
generate_tracker_workbook.py
Generates tracker_dashboard.xlsx from the CSV seed files in this repo.
Requirements:
  pip install pandas openpyxl xlsxwriter
Run:
  python generate_tracker_workbook.py
"""
import pandas as pd
from pathlib import Path
import xlsxwriter

BASE_DIR = Path(__file__).resolve().parent
CSV_TRANSACTIONS = BASE_DIR / 'tracker_transactions.csv'
CSV_HABITS = BASE_DIR / 'tracker_habits.csv'
CSV_RESOLUTIONS = BASE_DIR / 'tracker_resolutions.csv'
CSV_BUDGET = BASE_DIR / 'tracker_budget.csv'
CSV_JOURNAL = BASE_DIR / 'tracker_journal.csv'
OUT_XLSX = BASE_DIR / 'tracker_dashboard.xlsx'


def main() -> None:
    # Read CSVs
    transactions = pd.read_csv(CSV_TRANSACTIONS, parse_dates=['Date'])
    habits = pd.read_csv(CSV_HABITS, parse_dates=['Date'])
    resolutions = pd.read_csv(CSV_RESOLUTIONS, parse_dates=['StartDate', 'TargetDate'])
    budget = pd.read_csv(CSV_BUDGET)
    journal = pd.read_csv(CSV_JOURNAL, parse_dates=['Date'])

    # Prepare workbook
    workbook = xlsxwriter.Workbook(str(OUT_XLSX))

    # Formats
    fmt_header = workbook.add_format({'bold': True, 'bg_color': '#0f1720', 'font_color': '#cbd5e1'})
    fmt_currency = workbook.add_format({'num_format': '₹#,##0.00', 'font_color': '#cbd5e1'})
    fmt_default = workbook.add_format({'font_color': '#e6eef8'})
    fmt_title = workbook.add_format({'bold': True, 'font_size': 14, 'font_color': '#ffffff'})

    # Helper to write dataframe as table
    def write_table(ws_name, df, startrow=0, startcol=0):
        ws = workbook.add_worksheet(ws_name)
        # write headers
        for c, col in enumerate(df.columns.tolist()):
            ws.write(startrow, startcol + c, col, fmt_header)
        # write data
        for r, row in enumerate(df.values.tolist()):
            for c, val in enumerate(row):
                if isinstance(val, (float, int)):
                    ws.write(
                        startrow + 1 + r,
                        startcol + c,
                        val,
                        fmt_currency if df.columns[c].lower() in ['amount', 'monthlybudget'] else fmt_default,
                    )
                elif isinstance(val, pd.Timestamp):
                    ws.write(startrow + 1 + r, startcol + c, val.strftime('%Y-%m-%d'), fmt_default)
                else:
                    ws.write(startrow + 1 + r, startcol + c, val if pd.notnull(val) else '', fmt_default)
        return ws

    # Write CSV tables
    write_table('Transactions', transactions)
    write_table('Habits', habits)
    write_table('Resolutions', resolutions)
    write_table('Budget', budget)
    write_table('Journal', journal)

    # Dashboard sheet
    dash = workbook.add_worksheet('Dashboard')
    # Set background color
    dash.set_tab_color('#0b1220')
    # Write KPIs
    # Compute totals in Python
    tx_type = transactions['Type'].astype(str).str.lower()
    total_income = transactions[tx_type == 'income']['Amount'].sum()
    total_expense = transactions[tx_type == 'expense']['Amount'].sum()
    budget_total = budget['MonthlyBudget'].sum()
    budget_remaining = budget_total - total_expense
    net = total_income - total_expense

    dash.write('A1', 'Total Income', fmt_title)
    dash.write('B1', total_income, fmt_currency)

    dash.write('A2', 'Total Expenses', fmt_title)
    dash.write('B2', total_expense, fmt_currency)

    dash.write('A3', 'Budget Total', fmt_title)
    dash.write('B3', budget_total, fmt_currency)

    dash.write('A4', 'Budget Remaining', fmt_title)
    dash.write('B4', budget_remaining, fmt_currency)

    dash.write('A5', 'Net', fmt_title)
    dash.write('B5', net, fmt_currency)

    # Category spend chart (pie)
    # Aggregate expense by category
    cat_spend = transactions[tx_type == 'expense'].groupby('Category')['Amount'].sum().reset_index()
    # write category data to hidden sheet for chart
    chart_sheet = workbook.add_worksheet('ChartData')
    for i, col in enumerate(cat_spend.columns):
        chart_sheet.write(0, i, col, fmt_header)
    for r, row in enumerate(cat_spend.values.tolist()):
        chart_sheet.write(1 + r, 0, row[0], fmt_default)
        chart_sheet.write(1 + r, 1, row[1], fmt_currency)

    if len(cat_spend) > 0:
        pie = workbook.add_chart({'type': 'pie'})
        pie.add_series(
            {
                'name': 'Spend by Category',
                'categories': f"=ChartData!$A$2:$A${1 + len(cat_spend)}",
                'values': f"=ChartData!$B$2:$B${1 + len(cat_spend)}",
            }
        )
        pie.set_title({'name': 'Spend by Category'})
        dash.insert_chart('D2', pie, {'x_offset': 10, 'y_offset': 10})
    else:
        dash.write('D2', 'No expense category data available.', fmt_default)

    # Monthly spend chart
    transactions['Month'] = transactions['Date'].dt.to_period('M').astype(str)
    mon = transactions[tx_type == 'expense'].groupby('Month')['Amount'].sum().reset_index()
    for i, col in enumerate(mon.columns):
        chart_sheet.write(0, 3 + i, col, fmt_header)
    for r, row in enumerate(mon.values.tolist()):
        chart_sheet.write(1 + r, 3, row[0], fmt_default)
        chart_sheet.write(1 + r, 4, row[1], fmt_currency)

    if len(mon) > 0:
        line = workbook.add_chart({'type': 'line'})
        line.add_series(
            {
                'name': 'Monthly Expense',
                'categories': f"=ChartData!$D$2:$D${1 + len(mon)}",
                'values': f"=ChartData!$E$2:$E${1 + len(mon)}",
            }
        )
        line.set_title({'name': 'Monthly Expense'})
        dash.insert_chart('D20', line, {'x_offset': 10, 'y_offset': 10})
    else:
        dash.write('D20', 'No monthly expense data available.', fmt_default)

    # Close workbook
    workbook.close()
    print('Generated', OUT_XLSX.name)


if __name__ == '__main__':
    main()
