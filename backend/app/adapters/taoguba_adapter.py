from app.adapters.scraper_base import ScraperBaseAdapter, ScraperSelectors


class TaogubaScraperAdapter(ScraperBaseAdapter):
    platform = "taoguba"
    name = "淘股吧"
    url_pattern = r"https?://(?:www\.)?taoguba\.com\.cn/blog/(\d+)"
    profile_url_template = "https://www.taoguba.com.cn/blog/{uid}"
    selectors = ScraperSelectors(
        item=".blog-list .blog-item",
        title="a",
        summary=".blog-summary|p",
        url_prefix="https://www.taoguba.com.cn",
    )
