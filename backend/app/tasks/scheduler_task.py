import asyncio
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, func

from app.models.source import Source
from app.models.subscription import Subscription
from app.tasks.celery_app import celery_app
from app.tasks.db import session_factory as _session_factory


async def _schedule_due_sources():
    async with _session_factory() as db:
        query = (
            select(Source.id, func.min(Subscription.fetch_interval).label("min_interval"), Source.last_fetched_at)
            .join(Subscription, Subscription.source_id == Source.id)
            .group_by(Source.id)
        )
        result = await db.execute(query)
        now = datetime.now(timezone.utc)

        for source_id, min_interval, last_fetched in result.all():
            if last_fetched is None or now >= last_fetched + timedelta(seconds=min_interval):
                from app.tasks.fetch_task import fetch_source
                fetch_source.delay(str(source_id))


@celery_app.task(name="app.tasks.scheduler_task.schedule_due_sources")
def schedule_due_sources():
    asyncio.run(_schedule_due_sources())
