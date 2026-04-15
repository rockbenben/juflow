from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class SourceInfo:
    """Result of resolving a URL into a content source."""
    platform: str
    platform_uid: str
    display_name: str
    home_url: str
    avatar_url: str | None = None
    adapter_type: str = ""
    adapter_config: dict = field(default_factory=dict)


@dataclass
class ArticleItem:
    """A fetched article from a source."""
    title: str
    url: str
    summary: str = ""
    content: str | None = None
    cover_image: str | None = None
    published_at: datetime | None = None


class BaseAdapter(ABC):
    """Interface that every platform adapter must implement."""

    platform: str
    name: str
    adapter_type: str

    @abstractmethod
    def detect(self, url: str) -> bool:
        ...

    @abstractmethod
    async def resolve(self, url: str) -> SourceInfo:
        ...

    @abstractmethod
    async def fetch(self, source: SourceInfo, cookies: str | None = None) -> list[ArticleItem]:
        ...

    async def fetch_full(self, article: ArticleItem, cookies: str | None = None) -> ArticleItem:
        return article
