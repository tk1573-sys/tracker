# Architecture Guide

## Overview

The platform follows a clean, layered architecture:

```
main.py (CLI entry point)
    │
    ├── scripts/utilities/   ← Cross-cutting: logging, config, data loading
    ├── scripts/analytics/   ← Pure analytics functions (finance, habits, health)
    ├── scripts/generators/  ← Output generators (Excel workbook)
    ├── scripts/automation/  ← Automation helpers (backup)
    └── scripts/ai/          ← AI/LLM integration layer (pluggable)
```

## Data Flow

```
data/raw/*.csv
    → scripts/utilities/data_loader.py  (load & validate)
    → scripts/analytics/*.py            (compute KPIs, summaries)
    → scripts/generators/excel_workbook.py  (generate .xlsx)
    → dashboards/excel/tracker_dashboard.xlsx
```

## Module Responsibilities

| Module | Responsibility |
|---|---|
| `data_loader.py` | Load CSVs, validate schemas |
| `finance.py` | KPI calculation, monthly summary, category spend |
| `habits.py` | Completion rate, streaks, weekly summary |
| `health.py` | BMI, weekly averages |
| `excel_workbook.py` | Multi-sheet styled Excel generation |
| `insights.py` | Rule-based + LLM-ready analytics narratives |
| `backup.py` | Timestamped CSV backup |
| `config_loader.py` | Centralised YAML config access |
| `logger.py` | Rotating file + console logging |

## Adding New Trackers

1. Add a new CSV to `data/raw/`
2. Register the file in `scripts/utilities/data_loader.py`
3. Create `scripts/analytics/new_module.py` with analysis functions
4. Add a sheet writer to `TrackerWorkbookGenerator` in `excel_workbook.py`
5. Add tests in `tests/`

## AI Integration

The `scripts/ai/insights.py` module is designed as a drop-in AI layer.
Replace the `# TODO: Replace with real LLM call` comments with actual
OpenAI / Anthropic / local-LLM API calls. No changes to other modules required.
