from fastapi import APIRouter

from app.api.v1.endpoints import auth, goals, habits, health, health_records, journal, reminders, transactions

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(transactions.router)
api_router.include_router(habits.router)
api_router.include_router(health_records.router)
api_router.include_router(journal.router)
api_router.include_router(goals.router)
api_router.include_router(reminders.router)
