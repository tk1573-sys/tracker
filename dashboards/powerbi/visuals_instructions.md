# Power BI Build Guide

## Step 1 — Import Data

1. Open Power BI Desktop.
2. **Home → Get Data → Text/CSV**.
3. Import each file from `data/raw/`:
   - `tracker_transactions.csv`
   - `tracker_habits.csv`
   - `tracker_resolutions.csv`
   - `tracker_budget.csv`
   - `tracker_journal.csv`
   - `tracker_health.csv`
   - `tracker_food.csv`
4. In Power Query: set correct data types for each column (Date as Date, Amount as Decimal, Done as Text, etc.).
5. Click **Close & Apply**.

## Step 2 — Create the Date Table

In **Modeling → New Table**:

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

Right-click the Date table → **Mark as Date Table** → select the `Date` column.

## Step 3 — Create Relationships

In **Model view**, create these relationships:

| From | To | Cardinality |
|---|---|---|
| `Transactions[Date]` | `Date[Date]` | Many-to-One |
| `Habits[Date]` | `Date[Date]` | Many-to-One |
| `Health[Date]` | `Date[Date]` | Many-to-One |
| `Journal[Date]` | `Date[Date]` | Many-to-One |

## Step 4 — Apply Theme

**View → Themes → Browse for themes** → select `dashboards/powerbi/theme.json`.

## Step 5 — Add DAX Measures

Open `dashboards/powerbi/measures.md` and add each measure group via **Modeling → New Measure**.

## Step 6 — Build Report Pages

### Page 1: Executive Dashboard
- 5 KPI cards: Total Income, Total Expenses, Net Savings, Savings Rate %, Habit Completion %
- Line chart: Monthly income vs expense trend
- Donut chart: Expense by category
- Gauge: Budget utilisation %

### Page 2: Finance Analytics
- Bar chart: Monthly expense by category
- Line chart: Running total expenses
- Table: Transactions with conditional formatting
- Slicer: Date range, Category, Type

### Page 3: Health Dashboard
- Line charts: Weight trend, Sleep trend, Steps trend
- Card: Latest BMI with category label
- Column chart: Mood score over time
- Gauge: Daily water intake vs 2L target

### Page 4: Habit Analytics
- Bar chart: Habit completion % per habit
- Heat-map table: Daily habit status (conditional formatting)
- Line chart: Weekly habit score trend

### Page 5: Resolution Tracker
- Gauge visuals for each resolution (progress vs target)
- Table: Resolution name, target, current, % complete, status
- KPI: Count of on-track resolutions

### Page 6: Journal Insights
- Table: Journal entries with mood colour coding
- Line chart: Mood score over time
- Card: Average mood score

### Page 7: Monthly Review
- Matrix: All KPIs by month
- Column chart: Monthly net savings
- Line chart: MoM expense growth %

## Step 7 — Navigation & Polish

1. Add navigation buttons between pages using **Insert → Buttons**.
2. Add **Bookmarks** for filtered views.
3. Enable **Drill-through** on Category for transaction details.
4. Add **Tooltips** to charts showing extra metrics on hover.
5. Save the report as `tracker_report.pbix`.
