import asyncio
from datetime import datetime, timezone, timedelta

from sqlalchemy import delete

from app.models.adapter_health_log import AdapterHealthLog
from app.tasks.celery_app import celery_app
from app.tasks.db import session_factory as _session_factory


async def _cleanup_health_logs():
    cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    async with _session_factory() as db:
        result = await db.execute(
            delete(AdapterHealthLog).where(AdapterHealthLog.created_at < cutoff)
        )
        await db.commit()
        print(f"[cleanup] Deleted {result.rowcount} health log entries older than 7 days")


@celery_app.task(name="app.tasks.cleanup_task.cleanup_health_logs")
def cleanup_health_logs():
    asyncio.run(_cleanup_health_logs())
