from app.adapters.rss_base import DirectRssBaseAdapter


class V2exRssAdapter(DirectRssBaseAdapter):
    platform = "v2ex"
    name = "V2EX"
    url_pattern = r"https?://(?:www\.)?v2ex\.com/member/([^/]+)"
    rss_url_template = "https://www.v2ex.com/feed/member/{uid}.xml"
    home_url_template = "https://www.v2ex.com/member/{uid}"
