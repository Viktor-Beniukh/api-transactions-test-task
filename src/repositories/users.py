from datetime import datetime

from fastapi import HTTPException, status

from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.database import models
from src.core.database.models.enums import Role

from src.schemas.users import UserCreate, UserUpdate


async def create_user(user: UserCreate, session: AsyncSession) -> models.User:
    new_user = models.User(username=user.username)

    session.add(new_user)

    await session.commit()
    await session.refresh(new_user)

    return new_user


async def get_user_by_id(user_id: int, session: AsyncSession) -> models.User | None:
    stmt = (
        select(models.User)
        .where(
            models.User.id == user_id,
            models.User.role == Role.user
        )
    )
    result: Result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    return user


async def get_user_by_id_with_transactions(user_id: int, session: AsyncSession) -> models.User | None:
    stmt = (
        select(models.User)
        .options(selectinload(models.User.transactions))
        .where(
            models.User.id == user_id,
            models.User.role == Role.user
        )
    )
    result: Result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    return user


async def get_user_by_username(username: str, session: AsyncSession) -> models.User | None:
    stmt = (
        select(models.User)
        .where(
            models.User.username == username,
            models.User.role == Role.user
        )
    )
    result: Result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    return user


async def get_all_users(session: AsyncSession) -> list[models.User]:
    stmt = (
        select(models.User)
        .options(selectinload(models.User.transactions))
        .where(models.User.role == Role.user)
    )
    result: Result = await session.execute(stmt)
    user = result.scalars().all()
    return list(user)


async def update_user(
    session: AsyncSession, user_update: UserUpdate, user_id: int
) -> models.User:
    user = await get_user_by_id(session=session, user_id=user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    updated_data = user_update.model_dump()

    for field, value in updated_data.items():
        setattr(user, field, value)

    user.updated_at = datetime.now()

    await session.commit()
    await session.refresh(user)

    return user


async def delete_user(session: AsyncSession, user_id: int) -> None:
    user = await get_user_by_id(session=session, user_id=user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    await session.delete(user)
    await session.commit()
