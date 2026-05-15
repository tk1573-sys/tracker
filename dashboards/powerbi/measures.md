# Power BI DAX Measures

## Finance Measures

```dax
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

Net Savings = [Total Income] - [Total Expenses]

Savings Rate % =
DIVIDE([Net Savings], [Total Income], 0) * 100

Budget Total = SUM('Budget'[MonthlyBudget])

Budget Remaining = [Budget Total] - [Total Expenses]

Budget Utilisation % =
DIVIDE([Total Expenses], [Budget Total], 0) * 100

Monthly Income =
CALCULATE(
    [Total Income],
    DATESMTD('Date'[Date])
)

Monthly Expenses =
CALCULATE(
    [Total Expenses],
    DATESMTD('Date'[Date])
)

YTD Income =
CALCULATE([Total Income], DATESYTD('Date'[Date]))

YTD Expenses =
CALCULATE([Total Expenses], DATESYTD('Date'[Date]))

MoM Expense Growth % =
VAR CurrMonth = [Monthly Expenses]
VAR PrevMonth = CALCULATE([Monthly Expenses], DATEADD('Date'[Date], -1, MONTH))
RETURN DIVIDE(CurrMonth - PrevMonth, PrevMonth, 0) * 100

Rolling 3M Expenses =
CALCULATE(
    [Total Expenses],
    DATESINPERIOD('Date'[Date], LASTDATE('Date'[Date]), -3, MONTH)
)
```

## Habit Measures

```dax
Habit Completion Rate =
DIVIDE(
    CALCULATE(COUNTROWS('Habits'), 'Habits'[Done] = "Yes"),
    COUNTROWS('Habits'),
    0
)

Habit Completion % = [Habit Completion Rate] * 100

Weekly Habit Score =
CALCULATE(
    [Habit Completion Rate],
    DATESINTHISWEEK()
)
```

## Health Measures

```dax
Avg Weight =
AVERAGEX('Health', 'Health'[Weight_kg])

Avg Sleep Hours =
AVERAGEX('Health', 'Health'[Sleep_Hours])

Avg Daily Steps =
AVERAGEX('Health', 'Health'[Steps])

Avg Mood Score =
AVERAGEX('Health', 'Health'[Mood_Score])

Avg Water Liters =
AVERAGEX('Health', 'Health'[Water_Liters])

Latest BMI =
CALCULATE(
    MAX('Health'[BMI]),
    LASTDATE('Health'[Date])
)
```

## Resolution Measures

```dax
Resolution Progress % =
AVERAGEX(
    'Resolutions',
    DIVIDE('Resolutions'[CurrentValue], 'Resolutions'[MetricTarget], 0)
) * 100

Resolutions On Track =
CALCULATE(
    COUNTROWS('Resolutions'),
    'Resolutions'[Status] = "On track"
)
```

## Date Table (Add via New Table in Power BI)

```dax
Date =
ADDCOLUMNS(
    CALENDARAUTO(),
    "Year", YEAR([Date]),
    "Month", FORMAT([Date], "MMM YYYY"),
    "MonthNum", MONTH([Date]),
    "Quarter", "Q" & QUARTER([Date]),
    "Week", WEEKNUM([Date]),
    "DayName", FORMAT([Date], "dddd"),
    "IsWeekend", IF(WEEKDAY([Date], 2) >= 6, TRUE, FALSE)
)
```
