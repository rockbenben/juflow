from app.adapters.scraper_base import ScraperBaseAdapter, ScraperSelectors


class JisiluScraperAdapter(ScraperBaseAdapter):
    platform = "jisilu"
    name = "集思录"
    url_pattern = r"https?://(?:www\.)?jisilu\.cn/people/([^/]+)"
    profile_url_template = "https://www.jisilu.cn/people/{uid}"
    selectors = ScraperSelectors(
        item=".aw-item",
        title=".aw-item-title a",
        summary=".aw-item-content",
        url_prefix="https://www.jisilu.cn",
    )
