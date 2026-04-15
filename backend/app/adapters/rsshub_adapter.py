from app.adapters.rsshub_base import RsshubBaseAdapter


class XueqiuRsshubAdapter(RsshubBaseAdapter):
    platform = "xueqiu"
    name = "雪球"
    url_pattern = r"https?://xueqiu\.com/(?:u/)?(\d+)"
    rsshub_route_template = "/xueqiu/user/{uid}"
    display_name_template = "雪球用户{uid}"
    home_url_template = "https://xueqiu.com/u/{uid}"
