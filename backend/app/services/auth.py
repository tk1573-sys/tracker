from app.core.security import get_password_hash, verify_password
from app.repositories.auth import AuthRepository
from app.schemas.auth import UserCreate


class AuthService:
    def __init__(self, repository: AuthRepository) -> None:
        self.repository = repository

    def authenticate_user(self, email: str, password: str):
        user = self.repository.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

    def create_user(self, payload: UserCreate):
        hashed_password = get_password_hash(payload.password)
        return self.repository.create_user(payload, hashed_password)
