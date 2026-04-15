from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models.user import User
from app.services.auth_service import decode_access_token

security = HTTPBearer(auto_error=False)


async def get_db(session: AsyncSession = Depends(get_session)):
    yield session


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    # 1. JWT Bearer token
    if credentials:
        user_id = decode_access_token(credentials.credentials)
        if user_id:
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if user:
                return user

    # 2. X-API-Key header (only accept via header, not query params, to avoid URL logging)
    api_key = request.headers.get("X-API-Key")
    if api_key:
        result = await db.execute(select(User).where(User.api_key == api_key))
        user = result.scalar_one_or_none()
        if user:
            return user

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication")
