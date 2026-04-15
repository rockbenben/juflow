from app.adapters.rsshub_base import RsshubBaseAdapter


class XiaohongshuRsshubAdapter(RsshubBaseAdapter):
    platform = "xiaohongshu"
    name = "小红书"
    url_pattern = r"https?://(?:www\.)?xiaohongshu\.com/user/profile/(\w+)"
    rsshub_route_template = "/xiaohongshu/user/{uid}"
    display_name_template = "小红书用户{uid}"
    home_url_template = "https://www.xiaohongshu.com/user/profile/{uid}"
