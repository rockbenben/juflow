from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.services.subscription_service import add_subscription

router = APIRouter(prefix="/onboarding", tags=["onboarding"])

RECOMMENDED_SOURCES = [
    {
        "category": "财经",
        "sources": [
            {"name": "但斌", "url": "https://xueqiu.com/u/1043230052", "platform": "xueqiu", "description": "东方港湾创始人，长期价值投资"},
            {"name": "释老毛", "url": "https://xueqiu.com/u/1466826683", "platform": "xueqiu", "description": "知名财经博主，深度行业分析"},
            {"name": "DAVID自由之路", "url": "https://www.jisilu.cn/people/DAVID", "platform": "jisilu", "description": "集思录知名量化投资者"},
        ],
    },
    {
        "category": "技术",
        "sources": [
            {"name": "阮一峰", "url": "https://blog.csdn.net/ruanyf", "platform": "csdn", "description": "科技爱好者周刊作者"},
            {"name": "掘金热门", "url": "https://juejin.cn/user/1714893868765373", "platform": "juejin", "description": "前端技术分享"},
        ],
    },
    {
        "category": "公众号",
        "sources": [
            {"name": "半佛仙人", "url": "半佛仙人", "platform": "wechat_mp", "description": "商业深度分析，幽默犀利"},
            {"name": "远川投资评论", "url": "远川投资评论", "platform": "wechat_mp", "description": "专业投资研究"},
        ],
    },
]


@router.get("/recommended")
async def get_recommended():
    return RECOMMENDED_SOURCES


@router.post("/batch-subscribe")
async def batch_subscribe(
    urls: list[str],
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    results = []
    for url in urls:
        try:
            await add_subscription(db, user.id, url)
            results.append({"url": url, "ok": True})
        except Exception as e:
            results.append({"url": url, "ok": False, "error": str(e)})
    return {"results": results}
