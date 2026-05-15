# Setup Guide

## Prerequisites

- Python 3.9 or higher
- pip

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-username/tracker.git
cd tracker

# 2. (Optional) Create a virtual environment
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

## Running the Generator

```bash
# Generate Excel workbook (default)
python main.py

# Generate with backup of raw CSVs
python main.py --backup

# Print analytics insights to console
python main.py --insights

# Specify a custom output path
python main.py --output /path/to/output.xlsx

# Enable debug logging
python main.py --log-level DEBUG
```

## Running Tests

```bash
pip install pytest
pytest tests/ -v
```

## Directory Layout

```
tracker/
├── data/raw/          ← Put your CSV data files here
├── dashboards/excel/  ← Generated .xlsx appears here
├── dashboards/powerbi/← Power BI assets
├── scripts/           ← Python source modules
├── config/            ← YAML configuration files
├── logs/              ← Auto-created log files
├── docs/              ← Documentation
└── tests/             ← Unit tests
```
