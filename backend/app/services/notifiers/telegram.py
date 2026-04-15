import httpx
from html import escape as html_escape
from app.services.notifiers.base import BaseNotifier

class TelegramNotifier(BaseNotifier):
    channel = "telegram"

    async def send(self, user_settings: dict, article, source) -> bool:
        bot_token = user_settings.get("telegram_bot_token")
        chat_id = user_settings.get("telegram_chat_id")
        if not bot_token or not chat_id:
            return False
        text = f"<b>{html_escape(source.display_name)}</b> 发布新文章\n\n<a href=\"{html_escape(article.url)}\">{html_escape(article.title)}</a>"
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"https://api.telegram.org/bot{bot_token}/sendMessage",
                json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"}, timeout=10)
            return resp.status_code == 200
