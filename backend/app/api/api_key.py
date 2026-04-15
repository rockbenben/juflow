import secrets

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.models.user import User

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/api-key")
async def get_api_key(user: User = Depends(get_current_user)):
    if user.api_key:
        return {"api_key": user.api_key[:8] + "***", "has_key": True}
    return {"api_key": None, "has_key": False}


@router.post("/api-key/regenerate")
async def regenerate_api_key(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    new_key = secrets.token_hex(32)
    user.api_key = new_key
    await db.commit()
    return {"api_key": new_key}
