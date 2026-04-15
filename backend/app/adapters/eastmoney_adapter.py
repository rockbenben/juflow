from app.adapters.rsshub_base import RsshubBaseAdapter


class EastmoneyRsshubAdapter(RsshubBaseAdapter):
    platform = "eastmoney"
    name = "东方财富股吧"
    url_pattern = r"https?://guba\.eastmoney\.com/people/(\w+)"
    rsshub_route_template = "/eastmoney/user/{uid}"
    display_name_template = "东方财富用户{uid}"
    home_url_template = "https://guba.eastmoney.com/people/{uid}"
