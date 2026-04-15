import asyncio

from celery import Celery
from celery.schedules import crontab
from celery.signals import worker_ready

from app.config import settings

celery_app = Celery("juflow", broker=settings.redis_url, backend=settings.redis_url)


@worker_ready.connect
def load_plugins_on_worker_start(**kwargs):
    """Load user-installed plugins into the adapter registry when the worker starts."""
    from sqlalchemy import select
    from app.adapters.plugin_loader import plugin_loader
    from app.models.installed_plugin import InstalledPlugin
    from app.tasks.db import session_factory

    async def _load():
        async with session_factory() as db:
            result = await db.execute(
                select(InstalledPlugin).where(InstalledPlugin.enabled == True)  # noqa: E712
            )
            names = [p.name for p in result.scalars().all()]
            if names:
                count = plugin_loader.load_all_enabled(names)
                print(f"[celery] Loaded {count} plugin(s): {names}")

    try:
        asyncio.run(_load())
    except Exception as e:
        print(f"[celery] Plugin loading failed (non-fatal): {e}")

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    beat_schedule={
        "schedule-due-sources": {
            "task": "app.tasks.scheduler_task.schedule_due_sources",
            "schedule": 30.0,
        },
        "flush-dnd-queue": {
            "task": "app.tasks.dnd_task.flush_dnd_queue",
            "schedule": 60.0,
        },
        "send-hourly-digest": {
            "task": "app.tasks.digest_task.send_hourly_digest",
            "schedule": 3600.0,
        },
        "send-daily-digest": {
            "task": "app.tasks.digest_task.send_daily_digest",
            "schedule": crontab(hour=8, minute=0),
        },
        "validate-cookies": {
            "task": "app.tasks.cookie_task.validate_cookies",
            "schedule": 21600.0,
        },
        "cleanup-health-logs": {
            "task": "app.tasks.cleanup_task.cleanup_health_logs",
            "schedule": crontab(hour=3, minute=0),
        },
    },
)

celery_app.autodiscover_tasks([
    "app.tasks.scheduler_task",
    "app.tasks.fetch_task",
    "app.tasks.notify_task",
    "app.tasks.dnd_task",
    "app.tasks.digest_task",
    "app.tasks.cookie_task",
    "app.tasks.cleanup_task",
])
