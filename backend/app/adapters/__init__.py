from app.adapters.registry import registry
from app.adapters.rss_adapter import CsdnRssAdapter, ZhihuRssAdapter
from app.adapters.rsshub_adapter import XueqiuRsshubAdapter
from app.adapters.v2ex_adapter import V2exRssAdapter
from app.adapters.juejin_adapter import JuejinRsshubAdapter
from app.adapters.weibo_adapter import WeiboRsshubAdapter
from app.adapters.jisilu_adapter import JisiluScraperAdapter
from app.adapters.taoguba_adapter import TaogubaScraperAdapter
from app.adapters.eastmoney_adapter import EastmoneyRsshubAdapter
from app.adapters.tonghuashun_adapter import TonghuashunScraperAdapter
from app.adapters.jiuquaner_adapter import JiuquanerScraperAdapter
from app.adapters.youzhiyouxing_adapter import YouzhiyouxingScraperAdapter
from app.adapters.wechat_mp_adapter import WechatMpRsshubAdapter
from app.adapters.xiaohongshu_adapter import XiaohongshuRsshubAdapter

registry.register(CsdnRssAdapter())
registry.register(ZhihuRssAdapter())
registry.register(XueqiuRsshubAdapter())
registry.register(V2exRssAdapter())
registry.register(JuejinRsshubAdapter())
registry.register(WeiboRsshubAdapter())
registry.register(JisiluScraperAdapter())
registry.register(TaogubaScraperAdapter())
registry.register(EastmoneyRsshubAdapter())
registry.register(TonghuashunScraperAdapter())
registry.register(JiuquanerScraperAdapter())
registry.register(YouzhiyouxingScraperAdapter())
registry.register(WechatMpRsshubAdapter())
registry.register(XiaohongshuRsshubAdapter())

__all__ = ["registry"]
