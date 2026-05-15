# 📊 Personal Analytics Platform

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green)
![Excel](https://img.shields.io/badge/Excel-Dashboard-brightgreen?logo=microsoftexcel)
![Power BI](https://img.shields.io/badge/Power%20BI-Analytics-yellow?logo=powerbi)
![Status](https://img.shields.io/badge/Status-Active-success)

> An AI-ready personal analytics platform that transforms your daily tracking data into professional Excel dashboards and Power BI reports — with a clean, modular Python architecture designed for future LLM integration.

---

## ✨ Features

- 📈 **Multi-sheet Excel Dashboard** — Automated, dark-themed workbook with 12 sheets covering finances, habits, health, food, journal, and resolutions
- 💰 **Finance Analytics** — KPI cards, monthly income/expense trends, category spend breakdown with charts
- 🏋️ **Health Tracker** — BMI, weight trend, sleep, steps, water intake, mood score analysis
- 🍽️ **Food & Nutrition** — Macro tracking (calories, protein, carbs, fat) with daily meal logs
- ✅ **Habit Analytics** — Completion rates, current streaks, weekly summary trends
- 🎯 **Resolution Tracker** — Progress % per resolution with status indicators
- 📔 **Daily Journal** — Mood-coded journal entries
- 🤖 **AI-Ready Insights** — Pluggable LLM layer for narrative analytics (OpenAI/Anthropic-ready)
- 📊 **Power BI Assets** — Complete DAX measures library, dark theme JSON, build guide
- 🔄 **Auto Backup** — Timestamped CSV backups before each run
- ⚙️ **YAML Configuration** — Fully configurable via `config/` without touching code

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.9+ |
| Data | pandas |
| Excel | XlsxWriter |
| Config | PyYAML |
| BI | Power BI Desktop |
| Testing | pytest |

---

## 🚀 Quick Start

```bash
# 1. Clone and install
git clone https://github.com/your-username/tracker.git
cd tracker
pip install -r requirements.txt

# 2. Generate Excel dashboard
python main.py

# 3. View insights in terminal
python main.py --insights

# 4. Run with backup
python main.py --backup
```

The generated workbook lands at `dashboards/excel/tracker_dashboard.xlsx`.

---

## 📁 Folder Structure

```
tracker/
├── main.py                         ← CLI entry point
├── requirements.txt
├── config/
│   ├── app_config.yaml             ← App settings (currency, paths, etc.)
│   ├── categories.yaml             ← Expense/income/habit categories
│   └── dashboard_config.yaml      ← Excel & Power BI layout config
├── data/
│   ├── raw/                        ← Source CSV files
│   ├── processed/                  ← Intermediate data (auto-generated)
│   └── exports/                    ← Backups and exports
├── dashboards/
│   ├── excel/                      ← Generated .xlsx workbook
│   └── powerbi/                    ← Theme, DAX measures, build guide
├── scripts/
│   ├── analytics/                  ← Finance, habits, health analytics
│   ├── generators/                 ← Excel workbook generator
│   ├── automation/                 ← Backup utilities
│   ├── utilities/                  ← Logger, config loader, data loader
│   └── ai/                         ← AI/LLM insights engine
├── tests/                          ← Unit tests (pytest)
├── docs/                           ← Setup, architecture, troubleshooting
└── assets/                         ← Screenshots, icons, themes
```

---

## 📊 Power BI

1. Open Power BI Desktop
2. Import CSVs from `data/raw/`
3. Apply theme: `dashboards/powerbi/theme.json`
4. Add DAX measures from `dashboards/powerbi/measures.md`
5. Follow the full guide: `dashboards/powerbi/visuals_instructions.md`

---

## 🤖 AI Integration

The `scripts/ai/insights.py` module is designed as a drop-in AI layer:

```python
from scripts.ai.insights import InsightsEngine

# Rule-based (default)
engine = InsightsEngine(data)
print(engine.spending_summary())

# With LLM (plug in any client)
import openai
engine = InsightsEngine(data, llm_client=openai.OpenAI())
print(engine.spending_summary())  # Returns LLM-generated narrative
```

---

## 🗺 Roadmap

- [ ] Streamlit web dashboard
- [ ] OpenAI GPT-4o narrative insights
- [ ] Automated monthly email reports
- [ ] Google Sheets sync
- [ ] Mobile-friendly PWA view
- [ ] Predictive spending forecasts

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
