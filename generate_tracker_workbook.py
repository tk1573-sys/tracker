"""
generate_tracker_workbook.py
Generates tracker_dashboard.xlsx from the CSV seed files in this repo.
Requirements:
  pip install pandas openpyxl xlsxwriter
Run:
  python generate_tracker_workbook.py
"""
import pandas as pd
from datetime import datetime
import xlsxwriter

# Read CSVs
transactions = pd.read_csv('tracker_transactions.csv', parse_dates=['Date'])
habits = pd.read_csv('tracker_habits.csv', parse_dates=['Date'])
resolutions = pd.read_csv('tracker_resolutions.csv', parse_dates=['StartDate','TargetDate'])
budget = pd.read_csv('tracker_budget.csv')
journal = pd.read_csv('tracker_journal.csv', parse_dates=['Date'])

# Prepare workbook
out_xlsx = 'tracker_dashboard.xlsx'
workbook = xlsxwriter.Workbook(out_xlsx)

# Formats
fmt_header = workbook.add_format({'bold': True, 'bg_color': '#0f1720', 'font_color': '#cbd5e1'})
fmt_currency = workbook.add_format({'num_format': '₹#,##0.00', 'font_color': '#cbd5e1'})
fmt_default = workbook.add_format({'font_color': '#e6eef8'})
fmt_title = workbook.add_format({'bold': True, 'font_size': 14, 'font_color': '#ffffff'})
fmt_pct = workbook.add_format({'num_format': '0.0%', 'font_color': '#e6eef8'})

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
                ws.write(startrow + 1 + r, startcol + c, val, fmt_currency if df.columns[c].lower() in ['amount','monthlybudget'] else fmt_default)
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
total_income = transactions[transactions['Type']=='Income']['Amount'].sum()
total_expense = transactions[transactions['Type']=='Expense']['Amount'].sum()
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
cat_spend = transactions[transactions['Type']=='Expense'].groupby('Category')['Amount'].sum().reset_index()
# write category data to hidden sheet for chart
chart_sheet = workbook.add_worksheet('ChartData')
for i, col in enumerate(cat_spend.columns):
    chart_sheet.write(0, i, col, fmt_header)
for r, row in enumerate(cat_spend.values.tolist()):
    chart_sheet.write(1 + r, 0, row[0], fmt_default)
    chart_sheet.write(1 + r, 1, row[1], fmt_currency)

pie = workbook.add_chart({'type': 'pie'})
pie.add_series({'name': 'Spend by Category', 'categories': "=ChartData!$A$2:$A${}".format(1+len(cat_spend)), 'values': "=ChartData!$B$2:$B${}".format(1+len(cat_spend))})
pie.set_title({'name': 'Spend by Category'})
dash.insert_chart('D2', pie, {'x_offset': 10, 'y_offset': 10})

# Monthly spend chart
transactions['Month'] = transactions['Date'].dt.to_period('M').astype(str)
mon = transactions[transactions['Type']=='Expense'].groupby('Month')['Amount'].sum().reset_index()
for i, col in enumerate(mon.columns):
    chart_sheet.write(0, 3 + i, col, fmt_header)
for r, row in enumerate(mon.values.tolist()):
    chart_sheet.write(1 + r, 3, row[0], fmt_default)
    chart_sheet.write(1 + r, 4, row[1], fmt_currency)

line = workbook.add_chart({'type': 'line'})
line.add_series({'name': 'Monthly Expense', 'categories': "=ChartData!$D$2:$D${}".format(1+len(mon)), 'values': "=ChartData!$E$2:$E${}".format(1+len(mon))})
line.set_title({'name': 'Monthly Expense'})
dash.insert_chart('D20', line, {'x_offset': 10, 'y_offset': 10})

# Close workbook
workbook.close()
print('Generated', out_xlsx)
