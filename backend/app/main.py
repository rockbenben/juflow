import asyncio
import json
import uuid

import redis.asyncio as aioredis
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy import select

from app.api.auth import router as auth_router
from app.api.subscriptions import router as subscriptions_router
from app.api.articles import router as articles_router
from app.api.ws import router as ws_router
from app.api.groups import router as groups_router
from app.api.tags import router as tags_router
from app.api.opml import router as opml_router
from app.api.cookies import router as cookies_router
from app.api.notifications import router as notifications_router
from app.api.api_key import router as api_key_router
from app.api.plugins import router as plugins_router
from app.api.health import router as health_router
from app.api.onboarding import router as onboarding_router
from app.config import settings
from app.services.notification_service import notify_manager

app = FastAPI(title="JuFlow", version="1.0.0")

from app.api.auth import limiter as auth_limiter
app.state.limiter = auth_limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Versioned API routes
app.include_router(auth_router, prefix="/api/v1")
app.include_router(subscriptions_router, prefix="/api/v1")
app.include_router(articles_router, prefix="/api/v1")
app.include_router(groups_router, prefix="/api/v1")
app.include_router(tags_router, prefix="/api/v1")
app.include_router(opml_router, prefix="/api/v1")
app.include_router(cookies_router, prefix="/api/v1")
app.include_router(notifications_router, prefix="/api/v1")
app.include_router(api_key_router, prefix="/api/v1")
app.include_router(plugins_router, prefix="/api/v1")
app.include_router(health_router, prefix="/api/v1")
app.include_router(onboarding_router, prefix="/api/v1")

# WebSocket — no version prefix
app.include_router(ws_router)


@app.api_route(
    "/api/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    include_in_schema=False,
)
async def api_compat(path: str, request: Request):
    query = str(request.url.query)
    target = f"/api/v1/{path}"
    if query:
        target = f"{target}?{query}"
    return RedirectResponse(url=target, status_code=307)


@app.on_event("startup")
async def load_enabled_plugins():
    from app.adapters.plugin_loader import plugin_loader
    from app.database import get_session
    from app.models.installed_plugin import InstalledPlugin

    async def _load():
        async for db in get_session():
            result = await db.execute(
                select(InstalledPlugin).where(InstalledPlugin.enabled == True)  # noqa: E712
            )
            plugins = result.scalars().all()
            enabled_names = [p.name for p in plugins]
            count = plugin_loader.load_all_enabled(enabled_names)
            if count:
                print(f"[startup] Loaded {count} plugin(s): {enabled_names}")

    try:
        await _load()
    except Exception as e:
        print(f"[startup] Plugin loading failed (non-fatal): {e}")


@app.on_event("startup")
async def start_redis_listener():
    async def listen():
        while True:
            try:
                r = aioredis.from_url(settings.redis_url)
                pubsub = r.pubsub()
                await pubsub.subscribe("juflow:new_articles")
                async for message in pubsub.listen():
                    if message["type"] == "message":
                        data = json.loads(message["data"])
                        user_ids = [uuid.UUID(uid) for uid in data.get("user_ids", [])]
                        msg_type = data.get("type", "new_article")
                        for uid in user_ids:
                            if msg_type == "cookie_expired":
                                await notify_manager.notify_user(uid, {
                                    "type": "cookie_expired",
                                    "platform": data.get("platform"),
                                    "message": data.get("message"),
                                })
                            else:
                                await notify_manager.notify_user(uid, {
                                    "type": "new_article",
                                    "article": data.get("article"),
                                })
            except Exception as e:
                print(f"[redis] Listener disconnected: {e}. Reconnecting in 5s...")
                await asyncio.sleep(5)

    asyncio.create_task(listen())


@app.get("/health")
async def health():
    return {"status": "ok"}
