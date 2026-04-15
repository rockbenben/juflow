import defusedxml.ElementTree as ET
from io import BytesIO
from sqlalchemy.ext.asyncio import AsyncSession
from app.adapters import registry
from app.services.subscription_service import add_subscription


async def import_opml(db: AsyncSession, user_id, file_content: bytes) -> dict:
    tree = ET.parse(BytesIO(file_content))
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
        adapter = registry.detect(url)
        if not adapter:
            skipped.append({"url": url, "title": title, "reason": "unsupported platform"})
            continue
        try:
            await add_subscription(db, user_id, url)
            imported += 1
        except ValueError:
            skipped.append({"url": url, "title": title, "reason": "already subscribed or error"})

    return {"imported": imported, "skipped": skipped}


def _get_feed_url(source) -> str | None:
    """Extract the feed URL from a source's adapter_config, if available."""
    config = source.adapter_config or {}
    if "rss_url" in config:
        return config["rss_url"]
    if "rsshub_route" in config:
        from app.config import settings
        return f"{settings.rsshub_url}{config['rsshub_route']}"
    return None


def _make_outline_attrs(sub) -> dict:
    attrs = {
        "type": "rss",
        "text": sub.custom_name or sub.source.display_name,
        "title": sub.custom_name or sub.source.display_name,
        "htmlUrl": sub.source.home_url,
    }
    feed_url = _get_feed_url(sub.source)
    if feed_url:
        attrs["xmlUrl"] = feed_url
    return attrs


def export_opml(subscriptions) -> str:
    root = ET.Element("opml", version="2.0")
    head = ET.SubElement(root, "head")
    ET.SubElement(head, "title").text = "JuFlow Subscriptions"
    body = ET.SubElement(root, "body")

    grouped = {}
    ungrouped = []
    for sub in subscriptions:
        if hasattr(sub, 'groups') and sub.groups:
            for g in sub.groups:
                grouped.setdefault(g.name, []).append(sub)
        else:
            ungrouped.append(sub)

    for group_name, subs in grouped.items():
        folder = ET.SubElement(body, "outline", text=group_name, title=group_name)
        for sub in subs:
            ET.SubElement(folder, "outline", **_make_outline_attrs(sub))

    for sub in ungrouped:
        ET.SubElement(body, "outline", **_make_outline_attrs(sub))

    return ET.tostring(root, encoding="unicode", xml_declaration=True)
