from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class TransactionBase(BaseModel):
    type: str
    amount: Decimal


class TransactionCreate(TransactionBase):
    pass


class TransactionPartialUpdate(BaseModel):
    type: str | None = None
    amount: Decimal | None = None


class TransactionResponse(TransactionBase):
    model_config = ConfigDict(from_attributes=True)

    created_at: datetime
    updated_at: datetime
    user_id: int
    id: int


class TransactionMessageResponse(BaseModel):
    message: str
