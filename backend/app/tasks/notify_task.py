import asyncio, uuid, json
from datetime import datetime, timezone
from sqlalchemy import select
from app.config import settings
from app.models.article import Article
from app.models.source import Source
from app.models.subscription import Subscription
from app.models.user import User
from app.models.push_subscription import PushSubscription
from app.services.notifiers.dispatcher import dispatcher
from app.tasks.celery_app import celery_app
from app.tasks.db import session_factory as _session_factory
import redis as redis_lib

def _in_dnd(user_settings):
    if not user_settings.get("dnd_enabled"):
        return False
    now = datetime.now(timezone.utc).strftime("%H:%M")
    start = user_settings.get("dnd_start", "22:00")
    end = user_settings.get("dnd_end", "08:00")
    if start <= end:
        return start <= now <= end
    return now >= start or now <= end

async def _notify(article_id: str, source_id: str):
    async with _session_factory() as db:
        article = (await db.execute(select(Article).where(Article.id == uuid.UUID(article_id)))).scalar_one_or_none()
        source = (await db.execute(select(Source).where(Source.id == uuid.UUID(source_id)))).scalar_one_or_none()
        if not article or not source:
            return

        subs = (await db.execute(
            select(Subscription).where(Subscription.source_id == source.id, Subscription.notify_enabled == True)  # noqa
        )).scalars().all()

        r = redis_lib.Redis.from_url(settings.redis_url)
        for sub in subs:
            user = (await db.execute(select(User).where(User.id == sub.user_id))).scalar_one()
            user_settings = user.settings or {}

            push_subs = (await db.execute(
                select(PushSubscription).where(PushSubscription.user_id == user.id)
            )).scalars().all()
            user_settings["push_subscriptions"] = [{"endpoint": p.endpoint, "p256dh": p.p256dh, "auth": p.auth} for p in push_subs]

            channels = sub.notify_channels or user_settings.get("notify_defaults", ["web"])

            if _in_dnd(user_settings) and not sub.dnd_exempt:
                r.rpush(f"juflow:dnd_pending:{user.id}", json.dumps({"article_id": article_id, "source_id": source_id, "channels": channels}, default=str))
                continue

            email_digest = user_settings.get("email_digest", "instant")
            if email_digest != "instant" and "email" in channels:
                r.rpush(f"juflow:email_digest:{user.id}", json.dumps({"article_id": article_id, "source_id": source_id}))
                channels = [c for c in channels if c != "email"]

            await dispatcher.dispatch(user_settings, channels, article, source)

            # WebSocket push always
            msg = {"type": "new_article", "article": {"id": str(article.id), "title": article.title,
                "summary": (article.summary or "")[:200], "url": article.url,
                "published_at": str(article.published_at),
                "source": {"platform": source.platform, "display_name": source.display_name}},
                "user_ids": [str(user.id)]}
            r.publish("juflow:new_articles", json.dumps(msg, default=str))
        r.close()

@celery_app.task(name="app.tasks.notify_task.notify_new_article")
def notify_new_article(article_id: str, source_id: str):
    asyncio.run(_notify(article_id, source_id))
