import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.base import ArticleItem
from app.models.article import Article
from app.models.source import Source
from app.services.article_service import store_articles, get_user_articles
from app.services.text_utils import looks_like_html, split_article_text, to_plain_text


@pytest_asyncio.fixture
async def source(db: AsyncSession) -> Source:
    s = Source(platform="test", platform_uid="u1", display_name="Test", home_url="https://test.com", adapter_type="rss")
    db.add(s)
    await db.commit()
    await db.refresh(s)
    return s


@pytest_asyncio.fixture
async def subscription(db: AsyncSession, test_user, source):
    from app.models.subscription import Subscription

    sub = Subscription(user_id=test_user.id, source_id=source.id, fetch_interval=300)
    db.add(sub)
    await db.commit()
    return sub


def test_plain_text_with_angle_brackets_is_kept_verbatim():
    summary = "价格从 <10元 涨到 >20元"

    text, content = split_article_text(summary, None)

    assert text == summary
    assert content is None


def test_plain_text_is_not_treated_as_markup():
    assert not looks_like_html("性能 <5ms> 的提升")
    assert looks_like_html("<p>正文</p>")


def test_html_summary_becomes_the_body():
    text, content = split_article_text('<p>你好，<a href="x">链接</a></p>', None)

    assert text == "你好，链接"
    assert content == '<p>你好，<a href="x">链接</a></p>'


def test_entities_in_plain_text_are_not_rewritten():
    assert to_plain_text("a &lt; b &gt; c") == "a &lt; b &gt; c"


def test_normalising_twice_changes_nothing():
    summary = "价格从 <10元 涨到 >20元"

    once, _ = split_article_text(summary, None)
    twice, _ = split_article_text(once, None)

    assert once == twice


@pytest.mark.asyncio
async def test_store_articles_keeps_plain_summary_intact(db, source):
    summary = "价格从 <10元 涨到 >20元"
    items = [ArticleItem(title="Post", url="https://test.com/plain", summary=summary)]

    await store_articles(db, source.id, items)

    row = (
        await db.execute(select(Article).where(Article.url == "https://test.com/plain"))
    ).scalar_one()
    assert row.summary == summary
    assert row.content is None


@pytest.mark.asyncio
async def test_stored_html_summary_is_read_back_as_text_and_body(db, test_user, source, subscription):
    items = [ArticleItem(title="Post", url="https://test.com/html", summary="<p>你好</p>")]

    await store_articles(db, source.id, items)

    articles, _ = await get_user_articles(db, test_user.id)
    assert articles[0]["summary"] == "你好"
    assert articles[0]["content"] == "<p>你好</p>"
