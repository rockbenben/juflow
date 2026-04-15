import re
from dataclasses import dataclass
from datetime import datetime, timezone

import httpx
from bs4 import BeautifulSoup

from app.adapters.base import BaseAdapter, SourceInfo, ArticleItem


@dataclass
class ScraperSelectors:
    """CSS selectors for extracting articles from a page.

    title and summary support pipe-separated fallback selectors:
    "a.title|a" means try "a.title" first, fall back to "a".
    """
    item: str = ".aw-item"
    title: str = ".aw-item-title a"
    summary: str = ".aw-item-content"
    url_prefix: str = ""


class ScraperBaseAdapter(BaseAdapter):
    """Base class for scraper-backed adapters. Subclasses declare config + selectors."""

    adapter_type = "scraper"

    # Subclass must set these:
    platform: str
    name: str
    url_pattern: str  # regex with one capture group for the uid
    profile_url_template: str  # e.g. "https://www.jisilu.cn/people/{uid}"
    selectors: ScraperSelectors = ScraperSelectors()

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
            display_name=uid,
            home_url=self.profile_url_template.format(uid=uid),
            adapter_type=self.adapter_type,
        )

    @staticmethod
    def _select_first(el, selector_str: str):
        """Try pipe-separated selectors in priority order: 'a.title|a' tries a.title first."""
        for sel in selector_str.split("|"):
            found = el.select_one(sel.strip())
            if found:
                return found
        return None

    async def fetch(self, source: SourceInfo, cookies: str | None = None) -> list[ArticleItem]:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        if cookies:
            headers["Cookie"] = cookies
        url = self.profile_url_template.format(uid=source.platform_uid)
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers, timeout=30)
            resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")
        articles = []
        for item in soup.select(self.selectors.item):
            title_el = self._select_first(item, self.selectors.title)
            if not title_el:
                continue
            title = title_el.get_text(strip=True)
            href = title_el.get("href", "")
            article_url = href if href.startswith("http") else f"{self.selectors.url_prefix}{href}"
            summary_el = self._select_first(item, self.selectors.summary)
            summary = summary_el.get_text(strip=True) if summary_el else ""
            articles.append(ArticleItem(
                title=title,
                url=article_url,
                summary=summary,
                published_at=datetime.now(timezone.utc),
            ))
        return articles
