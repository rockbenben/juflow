import asyncio, json
import redis as redis_lib
from sqlalchemy import select
from app.config import settings
from app.models.user import User
from app.tasks.celery_app import celery_app
from app.tasks.notify_task import _in_dnd
from app.tasks.db import session_factory as _session_factory

async def _flush_dnd():
    r = redis_lib.Redis.from_url(settings.redis_url)
    async with _session_factory() as db:
        users = (await db.execute(select(User))).scalars().all()
        for user in users:
            if _in_dnd(user.settings or {}):
                continue
            key = f"juflow:dnd_pending:{user.id}"
            while r.llen(key) > 0:
                raw = r.lpop(key)
                if raw:
                    data = json.loads(raw)
                    from app.tasks.notify_task import notify_new_article
                    notify_new_article.delay(data["article_id"], data["source_id"])
    r.close()

@celery_app.task(name="app.tasks.dnd_task.flush_dnd_queue")
def flush_dnd_queue():
    asyncio.run(_flush_dnd())
