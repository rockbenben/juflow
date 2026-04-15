import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.subscription import SubscriptionCreate, SubscriptionResponse, SubscriptionUpdate
from app.services.subscription_service import add_subscription, list_subscriptions, delete_subscription, update_subscription

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.post("/", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_subscription(
    data: SubscriptionCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        sub = await add_subscription(db, user.id, data.url, data.fetch_interval, data.notify_enabled)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return sub


@router.get("/", response_model=list[SubscriptionResponse])
async def get_subscriptions(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await list_subscriptions(db, user.id)


@router.put("/{subscription_id}", response_model=SubscriptionResponse)
async def patch_subscription(
    subscription_id: uuid.UUID,
    data: SubscriptionUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    sub = await update_subscription(db, user.id, subscription_id, data)
    if not sub:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found")
    return sub


@router.delete("/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_subscription(
    subscription_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    deleted = await delete_subscription(db, user.id, subscription_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found")
