import httpx
from app.services.notifiers.base import BaseNotifier

class WechatNotifier(BaseNotifier):
    channel = "wechat"

    async def send(self, user_settings: dict, article, source) -> bool:
        webhook = user_settings.get("wechat_webhook")
        if not webhook:
            return False
        content = f"**{source.display_name}** 发布新文章\n\n[{article.title}]({article.url})\n\n{(article.summary or '')[:100]}"
        async with httpx.AsyncClient() as client:
            resp = await client.post(webhook, json={"msgtype": "markdown", "markdown": {"content": content}}, timeout=10)
            return resp.status_code == 200
