from app.adapters.scraper_base import ScraperBaseAdapter, ScraperSelectors


class YouzhiyouxingScraperAdapter(ScraperBaseAdapter):
    platform = "youzhiyouxing"
    name = "有知有行"
    url_pattern = r"https?://(?:www\.)?youzhiyouxing\.cn/people/(\w+)"
    profile_url_template = "https://youzhiyouxing.cn/people/{uid}"
    selectors = ScraperSelectors(
        item=".topic-item",
        title="a.topic-title|a",
        summary=".topic-summary|p",
        url_prefix="https://youzhiyouxing.cn",
    )
