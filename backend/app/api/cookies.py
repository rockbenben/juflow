from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.services.cookie_service import save_cookie, list_cookies, delete_cookie

router = APIRouter(prefix="/cookies", tags=["cookies"])


class CookieCreate(BaseModel):
    platform: str
    cookie_string: str


@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_cookie(data: CookieCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await save_cookie(db, user.id, data.platform, data.cookie_string)
    return {"ok": True}


@router.get("/")
async def get_cookies(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await list_cookies(db, user.id)


@router.delete("/{platform}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_cookie(platform: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    deleted = await delete_cookie(db, user.id, platform)
    if not deleted:
        raise HTTPException(status_code=404, detail="Cookie not found")
