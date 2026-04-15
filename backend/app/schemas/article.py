import uuid
from datetime import datetime
from pydantic import BaseModel

from app.schemas.source import SourceResponse


class ArticleResponse(BaseModel):
    id: uuid.UUID
    title: str
    summary: str
    content: str | None = None
    url: str
    cover_image: str | None = None
    published_at: datetime
    source: SourceResponse
    is_read: bool = False
    is_favorited: bool = False
    is_read_later: bool = False

    model_config = {"from_attributes": True}


class ArticleListResponse(BaseModel):
    articles: list[ArticleResponse]
    total: int


class ArticleMarkRead(BaseModel):
    is_read: bool


class ArticleToggleFavorite(BaseModel):
    is_favorited: bool


class ArticleToggleReadLater(BaseModel):
    is_read_later: bool
