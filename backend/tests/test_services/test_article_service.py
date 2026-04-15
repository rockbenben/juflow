import uuid
from datetime import datetime, timezone

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.base import ArticleItem
from app.models.source import Source
from app.models.subscription import Subscription
from app.services.article_service import store_articles, get_user_articles, mark_article_read


@pytest_asyncio.fixture
async def source(db: AsyncSession) -> Source:
    s = Source(platform="test", platform_uid="u1", display_name="Test", home_url="https://test.com", adapter_type="rss")
    db.add(s)
    await db.commit()
    await db.refresh(s)
    return s


@pytest_asyncio.fixture
async def subscription(db: AsyncSession, test_user, source) -> Subscription:
    sub = Subscription(user_id=test_user.id, source_id=source.id, fetch_interval=300)
    db.add(sub)
    await db.commit()
    return sub


@pytest.mark.asyncio
async def test_store_articles_dedup(db, source):
    items = [ArticleItem(title="Post 1", url="https://test.com/1", published_at=datetime.now(timezone.utc))]
    new1 = await store_articles(db, source.id, items)
    assert len(new1) == 1
    new2 = await store_articles(db, source.id, items)
    assert len(new2) == 0


@pytest.mark.asyncio
async def test_get_user_articles(db, test_user, source, subscription):
    items = [ArticleItem(title=f"Post {i}", url=f"https://test.com/{i}", published_at=datetime.now(timezone.utc)) for i in range(3)]
    await store_articles(db, source.id, items)
    articles, total = await get_user_articles(db, test_user.id)
    assert total == 3
    assert len(articles) == 3


@pytest.mark.asyncio
async def test_mark_read(db, test_user, source, subscription):
    items = [ArticleItem(title="Read Test", url="https://test.com/read", published_at=datetime.now(timezone.utc))]
    new_articles = await store_articles(db, source.id, items)
    await mark_article_read(db, test_user.id, new_articles[0].id, True)
    articles, _ = await get_user_articles(db, test_user.id)
    assert articles[0]["is_read"] is True
