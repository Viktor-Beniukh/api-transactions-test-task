from fastapi import HTTPException, Header, status
from sqlalchemy import select

from src.core.database.db_settings.db_helper import db_dependency
from src.core.database.models import AdminToken


async def get_current_admin(session: db_dependency, token: str = Header(...)) -> AdminToken:
    result = await session.execute(select(AdminToken).where(AdminToken.token == token))
    db_token = result.scalars().first()
    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token or missing",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return db_token
