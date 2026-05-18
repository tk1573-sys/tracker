from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.errors import ConflictError, UnauthorizedError
from app.core.security import create_access_token
from app.db.session import get_db
from app.models.user import User
from app.repositories.auth import AuthRepository
from app.schemas.auth import Token, UserCreate, UserRead
from app.services.auth import AuthService

router = APIRouter()


def get_service(db: Session) -> AuthService:
    return AuthService(AuthRepository(db))


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)) -> UserRead:
    service = get_service(db)
    existing = service.repository.get_by_email(str(payload.email))
    if existing:
        raise ConflictError("Email already registered")
    return service.create_user(payload)


@router.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> Token:
    user = get_service(db).authenticate_user(form_data.username, form_data.password)
    if not user:
        raise UnauthorizedError("Invalid credentials")
    access_token = create_access_token(subject=user.email)
    return Token(access_token=access_token)


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)) -> UserRead:
    return current_user
