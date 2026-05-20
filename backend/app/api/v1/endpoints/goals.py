from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_active_mode_id, get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.goals import (
    ExecutionPhaseCreate,
    ExecutionPhaseRead,
    GoalCreate,
    GoalRead,
    GoalUpdate,
    MilestoneCreate,
    MilestoneRead,
    MilestoneUpdate,
    ProjectCreate,
    ProjectRead,
    ProjectUpdate,
)
from app.services.goals import (
    add_execution_phase,
    add_milestone,
    create_goal,
    create_project,
    list_goals,
    list_projects,
    update_goal,
    update_milestone,
    update_project,
)

router = APIRouter()


@router.get("/projects", response_model=list[ProjectRead])
def get_projects(
    include_all_modes: bool = Query(default=False),
    active_mode_id: int = Depends(get_active_mode_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ProjectRead]:
    return list_projects(db, user_id=current_user.id, mode_id=active_mode_id, include_all_modes=include_all_modes)


@router.post("/projects", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def add_project(
    payload: ProjectCreate,
    active_mode_id: int = Depends(get_active_mode_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectRead:
    return create_project(db, user_id=current_user.id, mode_id=active_mode_id, payload=payload)


@router.patch("/projects/{project_id}", response_model=ProjectRead)
def patch_project(
    project_id: int,
    payload: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectRead:
    project = update_project(db, user_id=current_user.id, project_id=project_id, payload=payload)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


@router.post("/projects/{project_id}/milestones", response_model=MilestoneRead, status_code=status.HTTP_201_CREATED)
def add_project_milestone(
    project_id: int,
    payload: MilestoneCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MilestoneRead:
    milestone = add_milestone(db, user_id=current_user.id, project_id=project_id, payload=payload)
    if not milestone:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return milestone


@router.patch("/milestones/{milestone_id}", response_model=MilestoneRead)
def patch_milestone(
    milestone_id: int,
    payload: MilestoneUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MilestoneRead:
    milestone = update_milestone(db, user_id=current_user.id, milestone_id=milestone_id, payload=payload)
    if not milestone:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Milestone not found")
    return milestone


@router.post("/projects/{project_id}/phases", response_model=ExecutionPhaseRead, status_code=status.HTTP_201_CREATED)
def add_project_phase(
    project_id: int,
    payload: ExecutionPhaseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ExecutionPhaseRead:
    phase = add_execution_phase(db, user_id=current_user.id, project_id=project_id, payload=payload)
    if not phase:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return phase


@router.get("", response_model=list[GoalRead])
def get_goals(
    include_all_modes: bool = Query(default=False),
    active_mode_id: int = Depends(get_active_mode_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[GoalRead]:
    return list_goals(db, user_id=current_user.id, mode_id=active_mode_id, include_all_modes=include_all_modes)


@router.post("", response_model=GoalRead, status_code=status.HTTP_201_CREATED)
def add_goal(
    payload: GoalCreate,
    active_mode_id: int = Depends(get_active_mode_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> GoalRead:
    return create_goal(db, user_id=current_user.id, mode_id=active_mode_id, payload=payload)


@router.patch("/{goal_id}", response_model=GoalRead)
def patch_goal(
    goal_id: int,
    payload: GoalUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> GoalRead:
    goal = update_goal(db, user_id=current_user.id, goal_id=goal_id, payload=payload)
    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    return goal
