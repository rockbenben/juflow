from app.adapters.scraper_base import ScraperBaseAdapter, ScraperSelectors


class TonghuashunScraperAdapter(ScraperBaseAdapter):
    platform = "tonghuashun"
    name = "同花顺"
    url_pattern = r"https?://t\.10jqka\.com\.cn/u/(\w+)"
    profile_url_template = "https://t.10jqka.com.cn/u/{uid}"
    selectors = ScraperSelectors(
        item=".feed-item",
        title="a.title|a",
        summary=".feed-content|p",
        url_prefix="https://t.10jqka.com.cn",
    )
