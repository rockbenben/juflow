import smtplib
from html import escape as html_escape
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings
from app.services.notifiers.base import BaseNotifier

class EmailNotifier(BaseNotifier):
    channel = "email"

    async def send(self, user_settings: dict, article, source) -> bool:
        email_addr = user_settings.get("email_address")
        digest_mode = user_settings.get("email_digest", "instant")
        if not email_addr or digest_mode != "instant":
            return False

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"[聚流] {source.display_name}: {article.title}"
        msg["From"] = settings.smtp_from
        msg["To"] = email_addr

        html = f"""<div style="font-family:sans-serif;max-width:600px;">
        <h2 style="color:#6c63ff;">{html_escape(article.title)}</h2>
        <p style="color:#888;">{html_escape(source.display_name)} · {html_escape(source.platform)}</p>
        <p>{html_escape((article.summary or '')[:200])}</p>
        <a href="{html_escape(article.url)}" style="color:#6c63ff;">阅读原文 →</a></div>"""
        msg.attach(MIMEText(html, "html"))

        try:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
                server.starttls()
                if settings.smtp_user:
                    server.login(settings.smtp_user, settings.smtp_password)
                server.send_message(msg)
            return True
        except Exception:
            return False
