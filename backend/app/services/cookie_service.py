import uuid
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.platform_cookie import PlatformCookie
from app.services.crypto import encrypt, decrypt


async def save_cookie(db: AsyncSession, user_id: uuid.UUID, platform: str, cookie_string: str) -> PlatformCookie:
    result = await db.execute(
        select(PlatformCookie).where(PlatformCookie.user_id == user_id, PlatformCookie.platform == platform))
    existing = result.scalar_one_or_none()
    encrypted = encrypt(cookie_string)
    if existing:
        existing.cookie_encrypted = encrypted
        existing.is_valid = True
        existing.last_validated_at = datetime.now(timezone.utc)
    else:
        existing = PlatformCookie(user_id=user_id, platform=platform, cookie_encrypted=encrypted,
            is_valid=True, last_validated_at=datetime.now(timezone.utc))
        db.add(existing)
    await db.commit()
    await db.refresh(existing)
    return existing


async def list_cookies(db: AsyncSession, user_id: uuid.UUID) -> list[dict]:
    result = await db.execute(select(PlatformCookie).where(PlatformCookie.user_id == user_id))
    return [{"platform": c.platform, "is_valid": c.is_valid, "last_validated_at": str(c.last_validated_at) if c.last_validated_at else None} for c in result.scalars()]


async def delete_cookie(db: AsyncSession, user_id: uuid.UUID, platform: str) -> bool:
    result = await db.execute(
        select(PlatformCookie).where(PlatformCookie.user_id == user_id, PlatformCookie.platform == platform))
    cookie = result.scalar_one_or_none()
    if not cookie:
        return False
    await db.delete(cookie)
    await db.commit()
    return True


async def get_decrypted_cookie(db: AsyncSession, user_id: uuid.UUID, platform: str) -> str | None:
    result = await db.execute(
        select(PlatformCookie).where(
            PlatformCookie.user_id == user_id,
            PlatformCookie.platform == platform,
            PlatformCookie.is_valid == True,  # noqa: E712
        ))
    cookie = result.scalars().first()
    if cookie:
        return decrypt(cookie.cookie_encrypted)
    return None
