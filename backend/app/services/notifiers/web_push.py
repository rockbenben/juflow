import json
from app.services.notifiers.base import BaseNotifier

class WebPushNotifier(BaseNotifier):
    channel = "web_push"

    async def send(self, user_settings: dict, article, source) -> bool:
        push_subs = user_settings.get("push_subscriptions", [])
        if not push_subs:
            return False
        try:
            from pywebpush import webpush, WebPushException
            from app.config import settings
            for sub in push_subs:
                try:
                    webpush(
                        subscription_info={"endpoint": sub["endpoint"], "keys": {"p256dh": sub["p256dh"], "auth": sub["auth"]}},
                        data=json.dumps({"title": f"{source.display_name} 发布新文章", "body": article.title, "url": f"/article/{article.id}"}),
                        vapid_private_key=settings.vapid_private_key,
                        vapid_claims={"sub": f"mailto:{settings.vapid_claim_email}"},
                    )
                except WebPushException:
                    continue
            return True
        except ImportError:
            return False
