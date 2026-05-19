from fastapi import APIRouter

from app.api.v1.endpoints import ai, auth, dashboard, health, journal, modes, reminders, schedules, tasks, trackers

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(modes.router, prefix="/modes", tags=["modes"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(reminders.router, prefix="/reminders", tags=["reminders"])
api_router.include_router(journal.router, prefix="/journal", tags=["journal"])
api_router.include_router(trackers.router, prefix="/trackers", tags=["trackers"])
api_router.include_router(schedules.router, prefix="/schedules", tags=["schedules"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
