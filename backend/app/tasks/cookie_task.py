import asyncio
import json
from datetime import datetime, timezone
from sqlalchemy import select
import redis as redis_lib
from app.config import settings
from app.models.platform_cookie import PlatformCookie
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
            was_valid = cookie.is_valid
            try:
                decrypted = decrypt(cookie.cookie_encrypted)
                adapter = adapters[-1]
                dummy = SourceInfo(platform=cookie.platform, platform_uid="validate", display_name="", home_url="")
                await adapter.fetch(dummy, cookies=decrypted)
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
