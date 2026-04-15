import re

from app.adapters.base import SourceInfo
from app.adapters.rsshub_base import RsshubBaseAdapter


class WechatMpRsshubAdapter(RsshubBaseAdapter):
    platform = "wechat_mp"
    name = "微信公众号"
    url_pattern = r"https?://mp\.weixin\.qq\.com/(?:s\?__biz=|cgi-bin/).*"
    rsshub_route_template = "/wechat/mp/{uid}"
    display_name_template = "{uid}"
    home_url_template = "https://mp.weixin.qq.com"

    async def resolve(self, url: str) -> SourceInfo:
        biz_match = re.search(r"__biz=([\w=]+)", url)
        name = biz_match.group(1) if biz_match else url.split("mp.weixin.qq.com")[-1].strip("/") or url
        return SourceInfo(
            platform=self.platform,
            platform_uid=name,
            display_name=name,
            home_url=url,
            adapter_type=self.adapter_type,
            adapter_config={"rsshub_route": f"/wechat/mp/{name}"},
        )

    async def resolve_by_name(self, name: str) -> SourceInfo:
        return SourceInfo(
            platform=self.platform,
            platform_uid=name,
            display_name=name,
            home_url="https://mp.weixin.qq.com",
            adapter_type=self.adapter_type,
            adapter_config={"rsshub_route": f"/wechat/mp/{name}"},
        )
