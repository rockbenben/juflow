import re
from datetime import datetime, timezone

import feedparser
import httpx

from app.adapters.base import BaseAdapter, SourceInfo, ArticleItem
from app.config import settings


class RsshubBaseAdapter(BaseAdapter):
    """Base class for RSSHub-backed adapters. Subclasses only need to declare config."""

    adapter_type = "rsshub"

    # Subclass must set these:
    platform: str
    name: str
    url_pattern: str  # regex with one capture group for the uid
    rsshub_route_template: str  # e.g. "/xueqiu/user/{uid}"
    display_name_template: str  # e.g. "雪球用户{uid}"
    home_url_template: str  # e.g. "https://xueqiu.com/u/{uid}"

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if hasattr(cls, "url_pattern") and isinstance(cls.url_pattern, str):
            cls._compiled_pattern = re.compile(cls.url_pattern)

    def detect(self, url: str) -> bool:
        return bool(self._compiled_pattern.match(url))

    async def resolve(self, url: str) -> SourceInfo:
        match = self._compiled_pattern.match(url)
        if not match:
            raise ValueError(f"Cannot parse {self.name} URL: {url}")
        uid = match.group(1)
        return SourceInfo(
            platform=self.platform,
            platform_uid=uid,
            display_name=self.display_name_template.format(uid=uid),
            home_url=self.home_url_template.format(uid=uid),
            adapter_type=self.adapter_type,
            adapter_config={"rsshub_route": self.rsshub_route_template.format(uid=uid)},
        )

    async def fetch(self, source: SourceInfo, cookies: str | None = None) -> list[ArticleItem]:
        route = source.adapter_config.get(
            "rsshub_route", self.rsshub_route_template.format(uid=source.platform_uid)
        )
        rsshub_url = f"{settings.rsshub_url}{route}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(rsshub_url, timeout=30)
            resp.raise_for_status()
        feed = feedparser.parse(resp.text)
        articles = []
        for entry in feed.entries:
            published = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            articles.append(ArticleItem(
                title=entry.get("title", ""),
                url=entry.get("link", ""),
                summary=entry.get("summary", ""),
                content=entry.get("content", [{}])[0].get("value") if entry.get("content") else None,
                published_at=published,
            ))
        return articles
