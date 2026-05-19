# FastAPI Backend Foundation (MyManager AI MVP)

Production-ready modular monolith backend for **MyManager AI**.

## Stack

- FastAPI
- SQLAlchemy 2.x
- Alembic migrations
- PostgreSQL/SQLite
- JWT auth

## Structure

- `app/api/v1/endpoints/`: domain routers (`auth`, `modes`, `tasks`, `reminders`, `schedules`, `journal`, `trackers`, `dashboard`, `ai`)
- `app/services/`: service layer and orchestration (`ai`, `dashboard`, `reminders`, worker)
- `app/models/`: SQLAlchemy models for productivity core + trackers + AI logs
- `alembic/`: schema migrations

## Local setup

```bash
cd backend
python -m pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

## Core API surface

- `GET /api/v1/health`
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/token`
- `GET /api/v1/modes`
- `POST /api/v1/modes/activate`
- `GET|POST /api/v1/tasks`
- `PATCH /api/v1/tasks/{task_id}`
- `GET|POST /api/v1/reminders`
- `GET|POST /api/v1/schedules`
- `GET|POST /api/v1/journal`
- `GET /api/v1/trackers/summary`
- `GET /api/v1/dashboard`
- `POST /api/v1/ai/command`

## Mode context

- Modes: `personal`, `work`, `academic`
- Pass `X-Mode-Id` header to override active mode
- Without header, active mode defaults to the user's selected mode

## Reminder automation

A built-in background worker runs every 60s by default to:
- mark due reminders as sent
- create/send follow-ups for overdue incomplete tasks

Configure with:

- `REMINDER_WORKER_ENABLED=true|false`
- `REMINDER_WORKER_INTERVAL_SECONDS=60`
