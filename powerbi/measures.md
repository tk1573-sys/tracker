DAX Measures to add in Power BI:

Total Income =
CALCULATE(
  SUM('Transactions'[Amount]),
  'Transactions'[Type] = "Income"
)

Total Expenses =
CALCULATE(
  SUM('Transactions'[Amount]),
  'Transactions'[Type] = "Expense"
)

Net = [Total Income] - [Total Expenses]

Budgeted Total = SUM('Budget'[MonthlyBudget])

Budget Remaining = [Budgeted Total] - [Total Expenses]

Habit Completion Rate = DIVIDE(CALCULATE(COUNTROWS('Habits'), 'Habits'[Done] = "Yes"), COUNTROWS('Habits'))

Resolution Progress (%) = AVERAGEX('Resolutions', DIVIDE('Resolutions'[CurrentValue],'Resolutions'[MetricTarget],0))
