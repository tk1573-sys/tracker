from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_active_mode_id, get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.command_center import (
    CommandCenterAISuggestion,
    CommandCenterDeadlineItem,
    CommandCenterFocusBlockItem,
    CommandCenterOverdueFocus,
    CommandCenterPriorityTask,
    CommandCenterProductivitySummary,
    CommandCenterStreakSummary,
    CommandCenterTodayOverview,
)
from app.services.command_center import (
    get_ai_suggestions,
    get_focus_blocks,
    get_overdue_focus,
    get_priority_tasks,
    get_productivity_summary,
    get_streak_summary,
    get_today_overview,
    get_upcoming_deadlines,
)

router = APIRouter()


@router.get("/today-overview", response_model=CommandCenterTodayOverview)
def today_overview(
    active_mode_id: int = Depends(get_active_mode_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CommandCenterTodayOverview:
    return get_today_overview(db, user_id=current_user.id, mode_id=active_mode_id)


@router.get("/overdue-focus", response_model=CommandCenterOverdueFocus)
def overdue_focus(
    active_mode_id: int = Depends(get_active_mode_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CommandCenterOverdueFocus:
    return get_overdue_focus(db, user_id=current_user.id, mode_id=active_mode_id)


@router.get("/priority-tasks", response_model=list[CommandCenterPriorityTask])
def priority_tasks(
    active_mode_id: int = Depends(get_active_mode_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[CommandCenterPriorityTask]:
    return get_priority_tasks(db, user_id=current_user.id, mode_id=active_mode_id)


@router.get("/ai-suggestions", response_model=list[CommandCenterAISuggestion])
def ai_suggestions(
    active_mode_id: int = Depends(get_active_mode_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[CommandCenterAISuggestion]:
    return get_ai_suggestions(db, user_id=current_user.id, mode_id=active_mode_id)


@router.get("/productivity-summary", response_model=CommandCenterProductivitySummary)
def productivity_summary(
    active_mode_id: int = Depends(get_active_mode_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CommandCenterProductivitySummary:
    return get_productivity_summary(db, user_id=current_user.id, mode_id=active_mode_id)


@router.get("/streak-summary", response_model=CommandCenterStreakSummary)
def streak_summary(
    active_mode_id: int = Depends(get_active_mode_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CommandCenterStreakSummary:
    return get_streak_summary(db, user_id=current_user.id, mode_id=active_mode_id)


@router.get("/upcoming-deadlines", response_model=list[CommandCenterDeadlineItem])
def upcoming_deadlines(
    active_mode_id: int = Depends(get_active_mode_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[CommandCenterDeadlineItem]:
    return get_upcoming_deadlines(db, user_id=current_user.id, mode_id=active_mode_id)


@router.get("/focus-blocks", response_model=list[CommandCenterFocusBlockItem])
def focus_blocks(
    active_mode_id: int = Depends(get_active_mode_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[CommandCenterFocusBlockItem]:
    return get_focus_blocks(db, user_id=current_user.id, mode_id=active_mode_id)
