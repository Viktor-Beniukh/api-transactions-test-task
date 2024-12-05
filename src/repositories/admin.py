import logging

from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

from sqlalchemy import select, delete
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import models
from src.core.database.models.enums import Role

from src.schemas.admin import AdminRegister
from src.services.security import verify_password, generate_admin_token, get_password_hash
from src.services.validation import validate_password

logger = logging.getLogger(__name__)


async def register_admin(admin: AdminRegister, session: AsyncSession) -> JSONResponse | models.User:
    try:
        validate_password(password=admin.password)
    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        return JSONResponse(content={"error": str(ve)}, status_code=422)

    hashed_password = get_password_hash(password=admin.password)

    new_admin = models.User(username=admin.username, hashed_password=hashed_password,)

    session.add(new_admin)

    await session.commit()
    await session.refresh(new_admin)

    new_admin.role = Role.admin
    await session.commit()

    return new_admin


async def get_admin_by_username(username: str, session: AsyncSession) -> models.User | None:
    stmt = select(models.User).where(models.User.username == username, models.User.role == Role.admin)
    result: Result = await session.execute(stmt)
    admin = result.scalar_one_or_none()
    return admin


async def get_admin_by_id(admin_id: int, session: AsyncSession) -> models.User | None:
    stmt = select(models.User).where(models.User.id == admin_id, models.User.role == Role.admin)
    result: Result = await session.execute(stmt)
    admin = result.scalar_one_or_none()
    return admin


async def get_admin_token(token: str, session: AsyncSession) -> models.AdminToken | None:
    stmt = select(models.AdminToken).where(models.AdminToken.token == token)
    result: Result = await session.execute(stmt)
    admin_token = result.scalar_one_or_none()
    return admin_token


async def login_admin(username: str, password: str, session: AsyncSession) -> str:
    admin = await get_admin_by_username(username=username, session=session)

    if not admin or not verify_password(password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid username or password"
        )

    token = generate_admin_token()

    admin_token = models.AdminToken(user_id=admin.id, token=token)
    session.add(admin_token)
    await session.commit()

    return token


# async def logout_admin(session: AsyncSession):
#     await session.execute(delete(models.AdminToken))
#
#     await session.commit()
#

async def logout_admin(token: str, session: AsyncSession):
    await session.execute(
        delete(models.AdminToken).where(models.AdminToken.token == token)
    )
    await session.commit()
