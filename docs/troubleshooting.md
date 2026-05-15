# Troubleshooting

## "ModuleNotFoundError: No module named 'pandas'"

Run: `pip install -r requirements.txt`

## "FileNotFoundError: CSV not found"

Ensure all CSV files are present in `data/raw/`. See `data/raw/` for the expected filenames.

## "Permission denied" writing the Excel file

Close any open `tracker_dashboard.xlsx` before running the generator.

## Log file not appearing

The `logs/` directory is created automatically on first run. Check `logs/app.log`.

## Power BI can't find the CSV files

Use absolute paths when importing in Power BI, or move the CSVs to a stable location.
