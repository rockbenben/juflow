from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.push_subscription import PushSubscription

router = APIRouter(prefix="/notifications", tags=["notifications"])

class PushSubscribeRequest(BaseModel):
    endpoint: str
    p256dh: str
    auth: str

class NotificationSettingsUpdate(BaseModel):
    notify_defaults: Optional[list[str]] = None
    dnd_enabled: Optional[bool] = None
    dnd_start: Optional[str] = None
    dnd_end: Optional[str] = None
    email_digest: Optional[str] = None
    email_address: Optional[str] = None
    wechat_webhook: Optional[str] = None
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None

@router.get("/push/vapid-key")
async def get_vapid_key():
    from app.config import settings
    return {"public_key": settings.vapid_public_key}


@router.post("/push/subscribe", status_code=201)
async def push_subscribe(data: PushSubscribeRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    existing = (await db.execute(select(PushSubscription).where(
        PushSubscription.user_id == user.id, PushSubscription.endpoint == data.endpoint
    ))).scalar_one_or_none()
    if not existing:
        ps = PushSubscription(user_id=user.id, endpoint=data.endpoint, p256dh=data.p256dh, auth=data.auth)
        db.add(ps)
        await db.commit()
    return {"ok": True}

@router.get("/settings")
async def get_notification_settings(user: User = Depends(get_current_user)):
    s = user.settings or {}
    return {
        "notify_defaults": s.get("notify_defaults", ["web"]),
        "dnd_enabled": s.get("dnd_enabled", False),
        "dnd_start": s.get("dnd_start", "22:00"),
        "dnd_end": s.get("dnd_end", "08:00"),
        "email_digest": s.get("email_digest", "instant"),
        "email_address": s.get("email_address", ""),
        "wechat_webhook": s.get("wechat_webhook", ""),
        "telegram_bot_token": s.get("telegram_bot_token", ""),
        "telegram_chat_id": s.get("telegram_chat_id", ""),
    }

@router.put("/settings")
async def update_notification_settings(data: NotificationSettingsUpdate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    s = user.settings or {}
    updates = data.model_dump(exclude_none=True)
    for key, value in updates.items():
        s[key] = value
    user.settings = s
    await db.commit()
    return {"ok": True}
