import asyncio
import time
import uuid
from datetime import datetime, timezone

from sqlalchemy import select

from app.adapters import registry
from app.adapters.base import SourceInfo
from app.models.adapter_health_log import AdapterHealthLog
from app.models.source import Source
from app.models.subscription import Subscription
from app.services.article_service import store_articles
from app.tasks.celery_app import celery_app
from app.tasks.db import session_factory as _session_factory


async def _fetch_source(source_id: str):
    async with _session_factory() as db:
        result = await db.execute(select(Source).where(Source.id == uuid.UUID(source_id)))
        source = result.scalar_one_or_none()
        if not source:
            return

        adapters = registry.get_adapters_by_platform(source.platform)
        if not adapters:
            return

        from app.services.cookie_service import get_decrypted_cookie
        # Get cookie from the first subscriber who has one for this platform
        sub_result = await db.execute(
            select(Subscription.user_id).where(Subscription.source_id == source.id).limit(1)
        )
        sub_user_id = sub_result.scalar_one_or_none()
        cookie = None
        if sub_user_id:
            cookie = await get_decrypted_cookie(db, sub_user_id, source.platform)

        source_info = SourceInfo(
            platform=source.platform,
            platform_uid=source.platform_uid,
            display_name=source.display_name,
            home_url=source.home_url,
            adapter_type=source.adapter_type,
            adapter_config=source.adapter_config,
        )

        # Capture scalar values now: store_articles may hit a concurrent-insert
        # IntegrityError and rollback, which expires the ORM `source` instance.
        # Reading expired attributes in plain async code afterwards raises
        # MissingGreenlet, so snapshot what we need before that can happen.
        source_pk = source.id
        source_display = source.display_name

        items = None
        used_adapter_type = None
        error_msg = None
        start_time = time.monotonic()

        for adapter in adapters:
            try:
                items = await adapter.fetch(source_info, cookies=cookie)
                used_adapter_type = adapter.adapter_type
                break
            except Exception as e:
                error_msg = str(e)
                print(f"[fetch] {adapter.adapter_type} failed for {source.platform}/{source.platform_uid}: {e}")
                continue

        elapsed = time.monotonic() - start_time

        new_articles = []
        if items is not None:
            new_articles = await store_articles(db, source.id, items)
            source.last_fetched_at = datetime.now(timezone.utc)

        # Write health log
        log = AdapterHealthLog(
            source_id=source_pk,
            adapter_type=used_adapter_type or "unknown",
            success=items is not None,
            error_message=error_msg if items is None else None,
            duration_ms=int(elapsed * 1000),
            articles_count=len(new_articles) if items is not None else 0,
        )
        db.add(log)
        await db.commit()

        if new_articles:
            print(f"[fetch] {source_display}: {len(new_articles)} new articles")
            for article in new_articles:
                from app.tasks.notify_task import notify_new_article
                notify_new_article.delay(str(article.id), str(source_pk))


@celery_app.task(name="app.tasks.fetch_task.fetch_source")
def fetch_source(source_id: str):
    asyncio.run(_fetch_source(source_id))
