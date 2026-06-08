import asyncio
import json
from datetime import datetime, timezone
from sqlalchemy import select
import redis as redis_lib
from app.config import settings
from app.models.platform_cookie import PlatformCookie
from app.models.source import Source
from app.models.subscription import Subscription
from app.services.crypto import decrypt
from app.adapters import registry
from app.adapters.base import SourceInfo
from app.tasks.celery_app import celery_app
from app.tasks.db import session_factory as _session_factory

# Platform display names for user-facing messages
_PLATFORM_NAMES = {
    "jisilu": "集思录", "taoguba": "淘股吧", "tonghuashun": "同花顺",
    "jiuquaner": "韭圈儿", "youzhiyouxing": "有知有行", "xiaohongshu": "小红书",
    "xueqiu": "雪球", "weibo": "微博", "zhihu": "知乎", "csdn": "CSDN",
}


async def _validate_cookies():
    r = redis_lib.Redis.from_url(settings.redis_url)
    async with _session_factory() as db:
        cookies = (await db.execute(select(PlatformCookie))).scalars().all()
        for cookie in cookies:
            adapters = registry.get_adapters_by_platform(cookie.platform)
            if not adapters:
                continue

            # Validate against a real source this user subscribes to on this
            # platform. Fetching a fake uid ("validate") just 404s and would
            # wrongly mark valid cookies as expired. If the user has no such
            # subscription, there's nothing meaningful to test — leave it as-is.
            sub_source = (await db.execute(
                select(Source)
                .join(Subscription, Subscription.source_id == Source.id)
                .where(Subscription.user_id == cookie.user_id, Source.platform == cookie.platform)
                .limit(1)
            )).scalar_one_or_none()
            if sub_source is None:
                continue

            was_valid = cookie.is_valid
            try:
                decrypted = decrypt(cookie.cookie_encrypted)
                adapter = adapters[-1]
                source_info = SourceInfo(
                    platform=sub_source.platform,
                    platform_uid=sub_source.platform_uid,
                    display_name=sub_source.display_name,
                    home_url=sub_source.home_url,
                    adapter_type=sub_source.adapter_type,
                    adapter_config=sub_source.adapter_config or {},
                )
                await adapter.fetch(source_info, cookies=decrypted)
                cookie.is_valid = True
            except Exception:
                cookie.is_valid = False

            cookie.last_validated_at = datetime.now(timezone.utc)

            # Notify user if cookie just became invalid
            if was_valid and not cookie.is_valid:
                platform_name = _PLATFORM_NAMES.get(cookie.platform, cookie.platform)
                r.publish("juflow:new_articles", json.dumps({
                    "type": "cookie_expired",
                    "platform": cookie.platform,
                    "message": f"你的{platform_name} Cookie 已过期，请前往设置更新",
                    "user_ids": [str(cookie.user_id)],
                }, default=str))

        await db.commit()
    r.close()


@celery_app.task(name="app.tasks.cookie_task.validate_cookies")
def validate_cookies():
    asyncio.run(_validate_cookies())
