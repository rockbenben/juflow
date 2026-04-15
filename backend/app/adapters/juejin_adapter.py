from app.adapters.rsshub_base import RsshubBaseAdapter


class JuejinRsshubAdapter(RsshubBaseAdapter):
    platform = "juejin"
    name = "掘金"
    url_pattern = r"https?://(?:www\.)?juejin\.cn/user/(\d+)"
    rsshub_route_template = "/juejin/posts/{uid}"
    display_name_template = "掘金用户{uid}"
    home_url_template = "https://juejin.cn/user/{uid}"
