from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.services import health_service

router = APIRouter(prefix="/admin/health", tags=["health"])


@router.get("/")
async def platform_health_overview(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await health_service.get_platform_health(db)


@router.get("/timeline")
async def health_timeline(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await health_service.get_timeline(db)


@router.get("/{platform}")
async def platform_health_detail(
    platform: str,
    limit: int = Query(100, ge=1, le=500),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await health_service.get_platform_logs(db, platform, limit=limit)
