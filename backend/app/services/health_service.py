from datetime import datetime, timezone, timedelta

from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.adapter_health_log import AdapterHealthLog
from app.models.source import Source


async def get_platform_health(db: AsyncSession) -> list[dict]:
    since = datetime.now(timezone.utc) - timedelta(hours=24)

    # Main aggregation: counts, success rate, avg duration per platform
    result = await db.execute(
        select(
            Source.platform,
            func.count(AdapterHealthLog.id).label("total"),
            func.sum(
                case((AdapterHealthLog.success == True, 1), else_=0)  # noqa: E712
            ).label("success_count"),
            func.avg(AdapterHealthLog.duration_ms).label("avg_duration_ms"),
        )
        .join(Source, AdapterHealthLog.source_id == Source.id)
        .where(AdapterHealthLog.created_at >= since)
        .group_by(Source.platform)
        .order_by(Source.platform)
    )
    rows = result.all()
    platforms = [row.platform for row in rows]

    # Batch fetch last error per platform (single query instead of N+1)
    last_errors: dict[str, str | None] = {p: None for p in platforms}
    if platforms:
        subq = (
            select(
                Source.platform,
                AdapterHealthLog.error_message,
                func.row_number().over(
                    partition_by=Source.platform,
                    order_by=AdapterHealthLog.created_at.desc(),
                ).label("rn"),
            )
            .join(Source, AdapterHealthLog.source_id == Source.id)
            .where(
                AdapterHealthLog.success == False,  # noqa: E712
                AdapterHealthLog.created_at >= since,
                Source.platform.in_(platforms),
            )
            .subquery()
        )
        err_result = await db.execute(
            select(subq.c.platform, subq.c.error_message).where(subq.c.rn == 1)
        )
        for platform, error_message in err_result.all():
            last_errors[platform] = error_message

    health = []
    for row in rows:
        total = row.total or 0
        success_count = int(row.success_count or 0)
        health.append({
            "platform": row.platform,
            "total": total,
            "success_count": success_count,
            "success_rate": round(success_count / total, 4) if total > 0 else 0.0,
            "avg_duration_ms": round(float(row.avg_duration_ms or 0), 2),
            "last_error": last_errors.get(row.platform),
        })
    return health


async def get_platform_logs(db: AsyncSession, platform: str, limit: int = 100) -> list[dict]:
    result = await db.execute(
        select(AdapterHealthLog, Source.platform_uid, Source.display_name)
        .join(Source, AdapterHealthLog.source_id == Source.id)
        .where(Source.platform == platform)
        .order_by(AdapterHealthLog.created_at.desc())
        .limit(limit)
    )
    rows = result.all()
    return [
        {
            "id": str(log.id),
            "source_id": str(log.source_id),
            "platform_uid": platform_uid,
            "display_name": display_name,
            "adapter_type": log.adapter_type,
            "success": log.success,
            "error_message": log.error_message,
            "duration_ms": log.duration_ms,
            "articles_count": log.articles_count,
            "created_at": log.created_at,
        }
        for log, platform_uid, display_name in rows
    ]


async def get_timeline(db: AsyncSession) -> list[dict]:
    since = datetime.now(timezone.utc) - timedelta(hours=24)
    result = await db.execute(
        select(
            func.date_trunc("hour", AdapterHealthLog.created_at).label("hour"),
            func.count(AdapterHealthLog.id).label("total"),
            func.sum(
                case((AdapterHealthLog.success == True, 1), else_=0)  # noqa: E712
            ).label("success_count"),
            func.sum(
                case((AdapterHealthLog.success == False, 1), else_=0)  # noqa: E712
            ).label("failure_count"),
        )
        .where(AdapterHealthLog.created_at >= since)
        .group_by(func.date_trunc("hour", AdapterHealthLog.created_at))
        .order_by(func.date_trunc("hour", AdapterHealthLog.created_at))
    )
    rows = result.all()
    return [
        {
            "hour": row.hour,
            "total": row.total or 0,
            "success_count": int(row.success_count or 0),
            "failure_count": int(row.failure_count or 0),
        }
        for row in rows
    ]
