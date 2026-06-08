from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_admin
from app.models.user import User
from app.services import health_service

router = APIRouter(prefix="/admin/health", tags=["health"])


@router.get("/")
async def platform_health_overview(
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    return await health_service.get_platform_health(db)


@router.get("/timeline")
async def health_timeline(
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    return await health_service.get_timeline(db)


@router.get("/{platform}")
async def platform_health_detail(
    platform: str,
    limit: int = Query(100, ge=1, le=500),
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    return await health_service.get_platform_logs(db, platform, limit=limit)
