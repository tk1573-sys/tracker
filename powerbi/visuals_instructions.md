Power BI build instructions
1. Open Power BI Desktop.
2. Get Data -> Text/CSV -> import the CSV files in this repo (Transactions, Habits, Resolutions, Budget, Journal).
3. Create a Date table (Modeling -> New Table):
   Date = CALENDARAUTO()
   Mark as Date table.
4. Create relationships:
   - Transactions[Date] -> Date[Date]
   - (Optionally) link other tables to Date on their Date columns.
5. Add the DAX measures from measures.md.
6. Apply the theme: View -> Themes -> Browse for powerbi/theme.json.
7. Build visuals: KPIs (Total Income, Total Expenses, Budget Remaining, Net), Line chart for Monthly Expense, Donut for Category Spend, Table for Journal.
8. Save report as tracker_report.pbix.
