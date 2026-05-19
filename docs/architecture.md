# Architecture Guide

## Overview

The repository now has two aligned layers:

1. **Analytics pipeline (existing)** from `main.py` + `scripts/` for CSV-based tracker analytics and dashboard workbook generation.
2. **MyManager AI backend (new MVP monolith)** in `backend/` for authenticated productivity workflows.

## Existing Analytics Layer (preserved)

```
main.py (CLI entry point)
    │
    ├── scripts/utilities/   ← logging, config, data loading
    ├── scripts/analytics/   ← finance, habits, health analytics
    ├── scripts/generators/  ← Excel workbook generation
    ├── scripts/automation/  ← backup helpers
    └── scripts/ai/          ← pluggable analytics insights
```

## MyManager AI Backend Layer (MVP)

```
backend/app/
├── api/v1/endpoints/   ← auth, modes, tasks, reminders, schedules, journal, trackers, dashboard, ai
├── services/           ← domain logic + AI orchestration + reminder worker
├── models/             ← SQLAlchemy entities for productivity + trackers + AI logs
├── schemas/            ← API DTOs
└── core/db             ← config, security, logging, DB session
```

### Core domains

- Auth & Users
- Mode management (`personal`, `work`, `academic`)
- Tasks & Subtasks
- Reminders & Follow-ups
- Scheduling blocks
- Journal & wellness
- Tracker summaries (finance/habit/health)
- AI command orchestration
- Dashboard aggregation

### Mode context

- All core records use `mode_id`.
- Active mode is resolved from user defaults, with request override through `X-Mode-Id`.
- Per-mode defaults include starter categories and follow-up automation behavior.

### AI workflow (MVP)

1. Receive chat command (`/api/v1/ai/command`).
2. Parse intent with rule-based parser (LLM adapter-ready).
3. Validate ambiguity (clarification response when needed).
4. Execute task/reminder creation in one DB transaction.
5. Log `ai_messages` and `ai_actions` for traceability.

### Reminder workflow (MVP)

- Background worker loop (default every 60s) processes:
  - due reminders (`pending -> sent`)
  - overdue-task follow-up generation
  - follow-up dispatch with retry/backoff policy

## Frontend architecture target (Next.js)

MVP frontend is planned as a **mobile-first Next.js app** with App Router and feature modules:

- `/dashboard`
- `/tasks`
- `/reminders`
- `/journal`
- `/trackers`
- `/assistant`

Shared state should cover:
- auth session
- active mode
- today counts and quick actions

## Mobile-first strategy

- Build responsive web UI first (single frontend codebase).
- Keep APIs and DTOs stable/mobile-friendly from day one.
- Reuse same backend endpoints later for React Native clients.
- Keep notification/auth flows API-driven for cross-client reuse.

## Implementation roadmap

1. Foundation: schema, migrations, modes, tasks/reminders CRUD
2. AI MVP: command parse + dispatch + clarifications
3. Automation: reminder/follow-up worker and policies
4. Dashboard + journal integration
5. Hardening: performance, auditability, API stabilization for mobile
