from app.adapters.base import SourceInfo
from app.adapters.rss_base import DirectRssBaseAdapter


class CsdnRssAdapter(DirectRssBaseAdapter):
    platform = "csdn"
    name = "CSDN"
    url_pattern = r"https?://blog\.csdn\.net/([^/]+)"
    rss_url_template = "https://blog.csdn.net/{uid}/rss/list"
    home_url_template = "https://blog.csdn.net/{uid}"


class ZhihuRssAdapter(DirectRssBaseAdapter):
    platform = "zhihu"
    name = "知乎专栏"
    url_pattern = r"https?://(?:www\.)?zhihu\.com/(?:people|column)/([^/]+)"
    rss_url_template = "https://www.zhihu.com/people/{uid}/posts"
    home_url_template = "https://www.zhihu.com/people/{uid}"

    async def resolve(self, url: str) -> SourceInfo:
        match = self._compiled_pattern.match(url)
        if not match:
            raise ValueError(f"Cannot parse Zhihu URL: {url}")
        uid = match.group(1)
        is_column = "/column/" in url
        return SourceInfo(
            platform=self.platform,
            platform_uid=uid,
            display_name=uid,
            home_url=f"https://www.zhihu.com/{'column' if is_column else 'people'}/{uid}",
            adapter_type=self.adapter_type,
            adapter_config={
                "rss_url": f"https://www.zhihu.com/column/{uid}/rss" if is_column
                else f"https://www.zhihu.com/people/{uid}/posts",
                "is_column": is_column,
            },
        )
