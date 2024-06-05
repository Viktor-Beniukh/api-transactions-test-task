from datetime import datetime

from fastapi import HTTPException, status

from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.database import models

from src.repositories import users as repository_users

from src.schemas.transactions import TransactionCreate, TransactionPartialUpdate


async def create_transaction(
    transaction: TransactionCreate, user_id: int, session: AsyncSession
) -> models.Transaction:
    user = await repository_users.get_user_by_id(user_id=user_id, session=session)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    new_transaction = models.Transaction(**transaction.model_dump(), user_id=user.id)

    session.add(new_transaction)

    await session.commit()
    await session.refresh(new_transaction)

    return new_transaction


async def get_transaction_by_id_and_user_id(
    transaction_id: int, user_id: int, session: AsyncSession
) -> models.Transaction | None:
    stmt = (
        select(models.Transaction)
        .where(
            models.Transaction.id == transaction_id,
            models.Transaction.user_id == user_id
        )
    )
    result: Result = await session.execute(stmt)
    transaction = result.scalar_one_or_none()
    return transaction


async def get_all_transactions_by_user_id(user_id: int, session: AsyncSession) -> list[models.Transaction]:
    stmt = (
        select(models.Transaction)
        .options(selectinload(models.Transaction.user))
        .where(models.Transaction.user_id == user_id)
    )
    result: Result = await session.execute(stmt)
    transactions = result.scalars().all()
    return list(transactions)


async def partial_update_transaction(
    session: AsyncSession, transaction_update: TransactionPartialUpdate, transaction_id: int, user_id: int
) -> models.Transaction:
    transaction = await get_transaction_by_id_and_user_id(
        session=session, transaction_id=transaction_id, user_id=user_id
    )

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found"
        )

    updated_data = transaction_update.model_dump(exclude_unset=True)

    for field, value in updated_data.items():
        setattr(transaction, field, value)

    transaction.updated_at = datetime.now()

    await session.commit()
    await session.refresh(transaction)

    return transaction


async def delete_transaction(session: AsyncSession, transaction_id: int, user_id: int) -> None:
    transaction = await get_transaction_by_id_and_user_id(
        session=session, transaction_id=transaction_id, user_id=user_id
    )

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found"
        )

    await session.delete(transaction)
    await session.commit()
