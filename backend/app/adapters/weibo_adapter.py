from app.adapters.rsshub_base import RsshubBaseAdapter


class WeiboRsshubAdapter(RsshubBaseAdapter):
    platform = "weibo"
    name = "微博"
    url_pattern = r"https?://(?:www\.)?weibo\.com/u/(\d+)"
    rsshub_route_template = "/weibo/user/{uid}"
    display_name_template = "微博用户{uid}"
    home_url_template = "https://weibo.com/u/{uid}"
