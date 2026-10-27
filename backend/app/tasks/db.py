import asyncio
from collections.abc import Callable, Coroutine
from typing import Any

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.config import settings

engine = create_async_engine(settings.database_url, pool_size=5, max_overflow=10)
session_factory = async_sessionmaker(engine, expire_on_commit=False)


def run_task(coro_factory: Callable[[], Coroutine[Any, Any, Any]]) -> Any:
    """Run a task coroutine in a fresh event loop and release its connections.

    Celery runs every task in its own event loop (``asyncio.run``), but the
    engine above is module-level and lives as long as the worker process.
    Connections pooled by an earlier task belong to that task's closed loop, so
    they are never handed back and never closed: each task opens a fresh set
    and orphans the previous one. Postgres then runs out of connection slots
    ("sorry, too many clients already") within ~40 minutes of a normal
    install — the fetcher stops pulling articles and the database stops
    accepting new clients.

    Disposing the pool inside the *same* loop closes every connection the task
    opened before the loop goes away, so the next task starts from an empty
    pool instead of leaking one connection per run.
    """

    async def _runner() -> Any:
        try:
            return await coro_factory()
        finally:
            await engine.dispose()

    return asyncio.run(_runner())
