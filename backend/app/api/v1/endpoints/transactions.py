from datetime import datetime

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.transaction import TransactionType
from app.models.user import User
from app.repositories.transactions import TransactionRepository
from app.schemas.transaction import TransactionCreate, TransactionList, TransactionRead, TransactionUpdate
from app.services.transactions import TransactionService

router = APIRouter(prefix="/transactions", tags=["transactions"])


def get_service(db: Session) -> TransactionService:
    return TransactionService(TransactionRepository(db))


@router.post("", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
def create_transaction(payload: TransactionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_service(db).create(current_user.id, payload)


@router.get("", response_model=TransactionList)
def list_transactions(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    tx_type: TransactionType | None = Query(default=None, alias="type"),
    category: str | None = Query(default=None),
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_service(db).list(current_user.id, page, size, tx_type, category, start_date, end_date)


@router.get("/{transaction_id}", response_model=TransactionRead)
def get_transaction(transaction_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_service(db).get(current_user.id, transaction_id)


@router.patch("/{transaction_id}", response_model=TransactionRead)
def update_transaction(
    transaction_id: int,
    payload: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_service(db).update(current_user.id, transaction_id, payload)


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(transaction_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    get_service(db).delete(current_user.id, transaction_id)
