from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Mode(Base):
    __tablename__ = "modes"
    __table_args__ = (UniqueConstraint("user_id", "name", name="uq_modes_user_name"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    is_active_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
