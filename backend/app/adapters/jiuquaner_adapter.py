from app.adapters.scraper_base import ScraperBaseAdapter, ScraperSelectors


class JiuquanerScraperAdapter(ScraperBaseAdapter):
    platform = "jiuquaner"
    name = "韭圈儿"
    url_pattern = r"https?://(?:www\.)?jiuquaner\.com/user/(\w+)"
    profile_url_template = "https://www.jiuquaner.com/user/{uid}"
    selectors = ScraperSelectors(
        item=".post-item",
        title="a.post-title|a",
        summary=".post-summary|p",
        url_prefix="https://www.jiuquaner.com",
    )
