from app.services.notifiers.web_push import WebPushNotifier
from app.services.notifiers.wechat import WechatNotifier
from app.services.notifiers.telegram import TelegramNotifier
from app.services.notifiers.email_notifier import EmailNotifier

_notifiers = {
    "web_push": WebPushNotifier(),
    "wechat": WechatNotifier(),
    "telegram": TelegramNotifier(),
    "email": EmailNotifier(),
}

class NotificationDispatcher:
    async def dispatch(self, user_settings: dict, channels: list[str], article, source) -> None:
        for ch in channels:
            notifier = _notifiers.get(ch)
            if notifier:
                try:
                    await notifier.send(user_settings, article, source)
                except Exception:
                    pass

dispatcher = NotificationDispatcher()
