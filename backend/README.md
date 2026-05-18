# FastAPI Backend Foundation

Production-ready backend starter for the tracker project.

## Structure

- `app/`: FastAPI app, API routes, core config/security/logging, DB, models, schemas, services
- `alembic/`: migrations
- `Dockerfile` + `docker-compose.yml`: containerized API + PostgreSQL
- `.env.example`: environment template

## Local setup

```bash
cd backend
python -m pip install -r requirements.txt
cp .env.example .env
```

## Run API

```bash
uvicorn app.main:app --reload
```

## Run migrations

```bash
alembic upgrade head
```

## Example endpoints

- `GET /api/v1/health`
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/token`
- `GET /api/v1/auth/me`

## Notes

Existing analytics scripts remain unchanged and still run from repository root using:

```bash
python main.py
```
