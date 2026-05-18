from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.transaction import TransactionType
from app.schemas.common import Pagination


class TransactionBase(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    category: str = Field(min_length=1, max_length=80)
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    type: TransactionType
    description: str | None = Field(default=None, max_length=2000)
    occurred_at: datetime


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=120)
    category: str | None = Field(default=None, min_length=1, max_length=80)
    amount: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    type: TransactionType | None = None
    description: str | None = Field(default=None, max_length=2000)
    occurred_at: datetime | None = None


class TransactionRead(TransactionBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class TransactionList(BaseModel):
    pagination: Pagination
    items: list[TransactionRead]
