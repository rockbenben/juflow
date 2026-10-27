import xml.etree.ElementTree as XmlET

import defusedxml.ElementTree as ET
from io import BytesIO
from sqlalchemy.ext.asyncio import AsyncSession
from app.adapters import registry
from app.services.subscription_service import add_subscription


async def import_opml(db: AsyncSession, user_id, file_content: bytes) -> dict:
    try:
        tree = ET.parse(BytesIO(file_content))
    except ET.ParseError:
        raise ValueError("无法解析 OPML 文件，请检查文件格式")
    root = tree.getroot()
    body = root.find("body")
    if body is None:
        return {"imported": 0, "skipped": []}

    imported = 0
    skipped = []

    for outline in body.iter("outline"):
        url = outline.get("xmlUrl") or outline.get("htmlUrl")
        title = outline.get("title") or outline.get("text", "")
        if not url:
            continue
        # A URL we cannot map to a platform is skipped, but a bare name (how a
        # WeChat public account is stored) is worth a try: add_subscription
        # resolves account names itself.
        if not registry.detect(url) and ("." in url or "://" in url):
            skipped.append({"url": url, "title": title, "reason": "不支持的平台"})
            continue
        try:
            await add_subscription(db, user_id, url)
            imported += 1
        except ValueError as e:
            skipped.append({"url": url, "title": title, "reason": str(e) or "已订阅或解析失败"})

    return {"imported": imported, "skipped": skipped}


def _public_source_url(source) -> str:
    """A public, re-importable address for a source.

    RSSHub routes point at this deployment's own RSSHub container
    (``http://rsshub:1200/...``), which no other reader — and not even this one
    after a rebuild — can reach, so the exported file has to carry the
    blogger's public page instead. Sources added by WeChat account name have
    no public page (their home URL is the bare platform root), so the account
    name is the only thing that identifies them.
    """
    home = (source.home_url or "").strip()
    # A home URL with more than just "scheme://host" identifies a specific page.
    if home and home.rstrip("/").count("/") > 2:
        return home
    return source.platform_uid or home


def _get_feed_url(source) -> str | None:
    """Extract the feed URL from a source's adapter_config, if available."""
    config = source.adapter_config or {}
    if "rsshub_route" in config:
        # Instance-specific route — not portable, so it is not exported.
        return None
    if "rss_url" in config:
        return config["rss_url"]
    return None


def _make_outline_attrs(sub) -> dict:
    attrs = {
        "type": "rss",
        "text": sub.custom_name or sub.source.display_name,
        "title": sub.custom_name or sub.source.display_name,
        "htmlUrl": sub.source.home_url,
    }
    feed_url = _get_feed_url(sub.source)
    attrs["xmlUrl"] = feed_url or _public_source_url(sub.source)
    return attrs


def export_opml(subscriptions) -> str:
    root = XmlET.Element("opml", version="2.0")
    head = XmlET.SubElement(root, "head")
    XmlET.SubElement(head, "title").text = "JuFlow Subscriptions"
    body = XmlET.SubElement(root, "body")

    grouped = {}
    ungrouped = []
    for sub in subscriptions:
        if hasattr(sub, 'groups') and sub.groups:
            for g in sub.groups:
                grouped.setdefault(g.name, []).append(sub)
        else:
            ungrouped.append(sub)

    for group_name, subs in grouped.items():
        folder = XmlET.SubElement(body, "outline", text=group_name, title=group_name)
        for sub in subs:
            XmlET.SubElement(folder, "outline", **_make_outline_attrs(sub))

    for sub in ungrouped:
        XmlET.SubElement(body, "outline", **_make_outline_attrs(sub))

    return XmlET.tostring(root, encoding="unicode", xml_declaration=True)
