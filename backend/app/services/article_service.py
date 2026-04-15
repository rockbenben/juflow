import hashlib
import uuid
from datetime import datetime, timezone

from sqlalchemy import select, func, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.adapters.base import ArticleItem
from app.models.article import Article
from app.models.source import Source
from app.models.subscription import Subscription
from app.models.user_article import UserArticle


def make_fingerprint(url: str, title: str) -> str:
    raw = f"{url}|{title}"
    return hashlib.sha256(raw.encode()).hexdigest()


async def store_articles(db: AsyncSession, source_id: uuid.UUID, items: list[ArticleItem]) -> list[Article]:
    new_articles = []
    for item in items:
        fp = make_fingerprint(item.url, item.title)
        existing = await db.execute(select(Article).where(Article.fingerprint == fp))
        if existing.scalar_one_or_none():
            continue
        article = Article(
            source_id=source_id,
            title=item.title,
            summary=item.summary,
            content=item.content,
            url=item.url,
            cover_image=item.cover_image,
            published_at=item.published_at or datetime.now(timezone.utc),
            fingerprint=fp,
        )
        db.add(article)
        new_articles.append(article)
    if new_articles:
        try:
            await db.commit()
        except IntegrityError:
            await db.rollback()
            # Concurrent insert won the race. Re-query to return what was actually stored.
            new_articles = []
    return new_articles


async def get_user_articles(
    db: AsyncSession,
    user_id: uuid.UUID,
    unread_only: bool = False,
    limit: int = 50,
    offset: int = 0,
    filter_type: str | None = None,
    q: str | None = None,
    source_id: uuid.UUID | None = None,
) -> tuple[list[dict], int]:
    sub_result = await db.execute(select(Subscription.source_id).where(Subscription.user_id == user_id))
    source_ids = [row[0] for row in sub_result.all()]
    if not source_ids:
        return [], 0

    base_conditions = [Article.source_id.in_(source_ids)]

    if source_id is not None:
        base_conditions.append(Article.source_id == source_id)

    if q:
        escaped_q = q.replace("%", r"\%").replace("_", r"\_")
        base_conditions.append(Article.title.ilike(f"%{escaped_q}%"))

    query = (
        select(Article)
        .where(*base_conditions)
        .options(selectinload(Article.source))
        .order_by(Article.published_at.desc())
    )

    count_query = select(func.count(Article.id)).where(*base_conditions)

    # Join UserArticle when needed
    needs_ua_join = unread_only or filter_type in ("favorited", "read_later")

    if needs_ua_join:
        query = query.outerjoin(
            UserArticle, and_(UserArticle.article_id == Article.id, UserArticle.user_id == user_id)
        )
        count_query = count_query.outerjoin(
            UserArticle, and_(UserArticle.article_id == Article.id, UserArticle.user_id == user_id)
        )

    if unread_only:
        query = query.where((UserArticle.is_read == False) | (UserArticle.is_read == None))  # noqa: E712
        count_query = count_query.where((UserArticle.is_read == False) | (UserArticle.is_read == None))  # noqa: E712

    if filter_type == "favorited":
        query = query.where(UserArticle.is_favorited == True)  # noqa: E712
        count_query = count_query.where(UserArticle.is_favorited == True)  # noqa: E712
    elif filter_type == "read_later":
        query = query.where(UserArticle.is_read_later == True)  # noqa: E712
        count_query = count_query.where(UserArticle.is_read_later == True)  # noqa: E712

    total = (await db.execute(count_query)).scalar() or 0
    result = await db.execute(query.limit(limit).offset(offset))
    articles = result.scalars().all()

    article_ids = [a.id for a in articles]
    ua_result = await db.execute(
        select(UserArticle).where(UserArticle.user_id == user_id, UserArticle.article_id.in_(article_ids))
    )
    ua_map = {ua.article_id: ua for ua in ua_result.scalars().all()}

    enriched = []
    for article in articles:
        ua = ua_map.get(article.id)
        data = {
            "id": article.id,
            "title": article.title,
            "summary": article.summary,
            "content": article.content,
            "url": article.url,
            "cover_image": article.cover_image,
            "published_at": article.published_at,
            "source": article.source,
            "is_read": ua.is_read if ua else False,
            "is_favorited": ua.is_favorited if ua else False,
            "is_read_later": ua.is_read_later if ua else False,
        }
        enriched.append(data)
    return enriched, total


async def mark_article_read(db: AsyncSession, user_id: uuid.UUID, article_id: uuid.UUID, is_read: bool) -> None:
    result = await db.execute(
        select(UserArticle).where(UserArticle.user_id == user_id, UserArticle.article_id == article_id)
    )
    ua = result.scalar_one_or_none()
    if ua:
        ua.is_read = is_read
        ua.read_at = datetime.now(timezone.utc) if is_read else None
    else:
        ua = UserArticle(
            user_id=user_id,
            article_id=article_id,
            is_read=is_read,
            read_at=datetime.now(timezone.utc) if is_read else None,
        )
        db.add(ua)
    await db.commit()


async def toggle_favorite(
    db: AsyncSession, user_id: uuid.UUID, article_id: uuid.UUID, is_favorited: bool
) -> None:
    result = await db.execute(
        select(UserArticle).where(UserArticle.user_id == user_id, UserArticle.article_id == article_id)
    )
    ua = result.scalar_one_or_none()
    if ua:
        ua.is_favorited = is_favorited
    else:
        ua = UserArticle(
            user_id=user_id,
            article_id=article_id,
            is_favorited=is_favorited,
        )
        db.add(ua)
    await db.commit()


async def toggle_read_later(
    db: AsyncSession, user_id: uuid.UUID, article_id: uuid.UUID, is_read_later: bool
) -> None:
    result = await db.execute(
        select(UserArticle).where(UserArticle.user_id == user_id, UserArticle.article_id == article_id)
    )
    ua = result.scalar_one_or_none()
    if ua:
        ua.is_read_later = is_read_later
    else:
        ua = UserArticle(
            user_id=user_id,
            article_id=article_id,
            is_read_later=is_read_later,
        )
        db.add(ua)
    await db.commit()
