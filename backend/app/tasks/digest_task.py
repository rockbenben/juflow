import asyncio, json, uuid, smtplib
from html import escape as html_escape
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import redis as redis_lib
from sqlalchemy import select
from app.config import settings
from app.models.user import User
from app.models.article import Article
from app.models.source import Source
from app.tasks.celery_app import celery_app
from app.tasks.db import session_factory as _session_factory

_MAX_DIGEST_ITEMS = 50

async def _send_digest(mode: str):
    r = redis_lib.Redis.from_url(settings.redis_url)
    async with _session_factory() as db:
        users = (await db.execute(select(User))).scalars().all()
        for user in users:
            us = user.settings or {}
            if us.get("email_digest") != mode:
                continue
            email_addr = us.get("email_address")
            if not email_addr:
                continue

            key = f"juflow:email_digest:{user.id}"
            items = []
            # Only drain up to the render cap; leave the remainder queued for the
            # next digest cycle instead of lpop-ing and discarding it.
            while len(items) < _MAX_DIGEST_ITEMS and r.llen(key) > 0:
                raw = r.lpop(key)
                if raw:
                    items.append(json.loads(raw))
            if not items:
                continue

            rows = ""
            for item in items:
                article = (await db.execute(select(Article).where(Article.id == uuid.UUID(item["article_id"])))).scalar_one_or_none()
                source = (await db.execute(select(Source).where(Source.id == uuid.UUID(item["source_id"])))).scalar_one_or_none()
                if article and source:
                    rows += f'<tr><td style="padding:8px;color:#888;">{html_escape(source.display_name)}</td><td style="padding:8px;"><a href="{html_escape(article.url)}" style="color:#6c63ff;">{html_escape(article.title)}</a></td></tr>'

            label = "每小时" if mode == "hourly" else "每日"
            html = f"""<div style="font-family:sans-serif;max-width:600px;background:#1a1a2e;padding:24px;border-radius:12px;">
            <h2 style="color:#6c63ff;">聚流 · {label}摘要</h2>
            <table style="width:100%;border-collapse:collapse;color:#dfe6e9;">{rows}</table></div>"""

            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"[聚流] {label}摘要 — {len(items)} 篇新文章"
            msg["From"] = settings.smtp_from
            msg["To"] = email_addr
            msg.attach(MIMEText(html, "html"))

            try:
                with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
                    server.starttls()
                    if settings.smtp_user:
                        server.login(settings.smtp_user, settings.smtp_password)
                    server.send_message(msg)
            except Exception as e:
                print(f"[digest] Failed: {e}")
    r.close()

@celery_app.task(name="app.tasks.digest_task.send_hourly_digest")
def send_hourly_digest():
    asyncio.run(_send_digest("hourly"))

@celery_app.task(name="app.tasks.digest_task.send_daily_digest")
def send_daily_digest():
    asyncio.run(_send_digest("daily"))
