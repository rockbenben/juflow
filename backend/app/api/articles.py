import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.article import (
    ArticleListResponse,
    ArticleResponse,
    ArticleMarkRead,
    ArticleToggleFavorite,
    ArticleToggleReadLater,
)
from app.services.article_service import (
    get_user_articles,
    mark_article_read,
    toggle_favorite,
    toggle_read_later,
)

router = APIRouter(prefix="/articles", tags=["articles"])


@router.get("/", response_model=ArticleListResponse)
async def list_articles(
    unread_only: bool = Query(False),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    filter: Optional[str] = Query(None, description="Filter type: 'favorited' or 'read_later'"),
    q: Optional[str] = Query(None, description="Search query (title match)"),
    source_id: Optional[uuid.UUID] = Query(None, description="Filter by source ID"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    articles, total = await get_user_articles(
        db, user.id, unread_only, limit, offset,
        filter_type=filter,
        q=q,
        source_id=source_id,
    )
    return ArticleListResponse(
        articles=[ArticleResponse.model_validate(a) for a in articles],
        total=total,
    )


@router.patch("/{article_id}/read")
async def toggle_read(
    article_id: uuid.UUID,
    data: ArticleMarkRead,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await mark_article_read(db, user.id, article_id, data.is_read)
    return {"ok": True}


@router.patch("/{article_id}/favorite")
async def toggle_article_favorite(
    article_id: uuid.UUID,
    data: ArticleToggleFavorite,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await toggle_favorite(db, user.id, article_id, data.is_favorited)
    return {"ok": True}


@router.patch("/{article_id}/read-later")
async def toggle_article_read_later(
    article_id: uuid.UUID,
    data: ArticleToggleReadLater,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await toggle_read_later(db, user.id, article_id, data.is_read_later)
    return {"ok": True}
