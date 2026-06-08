import ipaddress
import socket
import uuid
from urllib.parse import urlparse

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.adapters import registry
from app.models.group import Group
from app.models.source import Source
from app.models.subscription import Subscription
from app.models.tag import Tag


def _is_blocked_ip(ip: ipaddress._BaseAddress) -> bool:
    return (
        ip.is_private or ip.is_loopback or ip.is_link_local
        or ip.is_reserved or ip.is_multicast or ip.is_unspecified
    )


def _validate_subscription_url(url: str) -> None:
    """Block SSRF attempts via internal/metadata URLs.

    Resolves the hostname and rejects it if *any* resolved address is internal,
    so hostnames pointing at private/metadata IPs are caught — not just literal
    IPs. (DNS rebinding between this check and the later fetch remains out of
    scope; pinning the resolved IP through to the HTTP client would be needed.)
    """
    parsed = urlparse(url)
    hostname = parsed.hostname or ""
    if not parsed.scheme or parsed.scheme not in ("http", "https"):
        raise ValueError("链接必须以 http 或 https 开头")
    if not hostname:
        raise ValueError("链接缺少有效域名")

    # Resolve to every address the host maps to and reject any internal one.
    try:
        addrinfos = socket.getaddrinfo(hostname, None)
    except socket.gaierror:
        # Unresolvable host can't reach an internal IP; the later fetch will fail.
        return
    for info in addrinfos:
        ip_str = info[4][0].split("%")[0]  # strip IPv6 scope id, e.g. fe80::1%eth0
        try:
            ip = ipaddress.ip_address(ip_str)
        except ValueError:
            continue
        if _is_blocked_ip(ip):
            raise ValueError("该链接指向内网地址，已拒绝")


async def add_subscription(
    db: AsyncSession, user_id: uuid.UUID, url: str, fetch_interval: int = 300, notify_enabled: bool = True
) -> Subscription:
    # Only validate URLs, not plain names (e.g. WeChat MP account names)
    if "://" in url or "." in url:
        _validate_subscription_url(url)
    adapter = registry.detect(url)
    if not adapter and "." not in url:
        wechat = registry.get_by_platform("wechat_mp")
        if wechat and hasattr(wechat, "resolve_by_name"):
            source_info = await wechat.resolve_by_name(url)
            result = await db.execute(
                select(Source).where(Source.platform == source_info.platform, Source.platform_uid == source_info.platform_uid)
            )
            source = result.scalar_one_or_none()
            if not source:
                source = Source(
                    platform=source_info.platform,
                    platform_uid=source_info.platform_uid,
                    display_name=source_info.display_name,
                    avatar_url=source_info.avatar_url,
                    home_url=source_info.home_url,
                    adapter_type=source_info.adapter_type,
                    adapter_config=source_info.adapter_config,
                )
                db.add(source)
                await db.flush()

            existing = await db.execute(
                select(Subscription).where(Subscription.user_id == user_id, Subscription.source_id == source.id)
            )
            if existing.scalar_one_or_none():
                raise ValueError("已经订阅过该来源")

            sub = Subscription(
                user_id=user_id,
                source_id=source.id,
                fetch_interval=max(fetch_interval, 60),
                notify_enabled=notify_enabled,
            )
            db.add(sub)
            await db.commit()

            result = await db.execute(
                select(Subscription).where(Subscription.id == sub.id).options(selectinload(Subscription.source))
            )
            return result.scalar_one()

    if not adapter:
        raise ValueError("暂不支持该链接，请粘贴受支持平台的博主主页地址")

    source_info = await adapter.resolve(url)

    result = await db.execute(
        select(Source).where(Source.platform == source_info.platform, Source.platform_uid == source_info.platform_uid)
    )
    source = result.scalar_one_or_none()
    if not source:
        source = Source(
            platform=source_info.platform,
            platform_uid=source_info.platform_uid,
            display_name=source_info.display_name,
            avatar_url=source_info.avatar_url,
            home_url=source_info.home_url,
            adapter_type=source_info.adapter_type,
            adapter_config=source_info.adapter_config,
        )
        db.add(source)
        await db.flush()

    existing = await db.execute(
        select(Subscription).where(Subscription.user_id == user_id, Subscription.source_id == source.id)
    )
    if existing.scalar_one_or_none():
        raise ValueError("Already subscribed to this source")

    sub = Subscription(
        user_id=user_id,
        source_id=source.id,
        fetch_interval=max(fetch_interval, 60),
        notify_enabled=notify_enabled,
    )
    db.add(sub)
    await db.commit()

    result = await db.execute(
        select(Subscription).where(Subscription.id == sub.id).options(selectinload(Subscription.source))
    )
    return result.scalar_one()


async def get_subscription_detail(
    db: AsyncSession, user_id: uuid.UUID, subscription_id: uuid.UUID
) -> dict | None:
    result = await db.execute(
        select(Subscription)
        .where(Subscription.id == subscription_id, Subscription.user_id == user_id)
        .options(
            selectinload(Subscription.source),
            selectinload(Subscription.groups),
            selectinload(Subscription.tags),
        )
    )
    sub = result.scalar_one_or_none()
    if not sub:
        return None
    return {
        "id": str(sub.id),
        "custom_name": sub.custom_name,
        "fetch_interval": sub.fetch_interval,
        "notify_enabled": sub.notify_enabled,
        "notify_channels": sub.notify_channels,
        "dnd_exempt": sub.dnd_exempt,
        "group_ids": [str(g.id) for g in sub.groups],
        "tag_ids": [str(t.id) for t in sub.tags],
    }


async def list_subscriptions(db: AsyncSession, user_id: uuid.UUID) -> list[Subscription]:
    result = await db.execute(
        select(Subscription)
        .where(Subscription.user_id == user_id)
        # groups is eager-loaded because export_opml() reads sub.groups; a lazy
        # load there would raise MissingGreenlet in the async request context.
        .options(selectinload(Subscription.source), selectinload(Subscription.groups))
        .order_by(Subscription.created_at.desc())
    )
    return list(result.scalars().all())


async def delete_subscription(db: AsyncSession, user_id: uuid.UUID, subscription_id: uuid.UUID) -> bool:
    result = await db.execute(
        select(Subscription).where(Subscription.id == subscription_id, Subscription.user_id == user_id)
    )
    sub = result.scalar_one_or_none()
    if not sub:
        return False
    await db.delete(sub)
    await db.commit()
    return True


async def update_subscription(
    db: AsyncSession,
    user_id: uuid.UUID,
    subscription_id: uuid.UUID,
    data,
) -> Subscription | None:
    result = await db.execute(
        select(Subscription)
        .where(Subscription.id == subscription_id, Subscription.user_id == user_id)
        .options(
            selectinload(Subscription.source),
            selectinload(Subscription.groups),
            selectinload(Subscription.tags),
        )
    )
    sub = result.scalar_one_or_none()
    if not sub:
        return None

    if data.custom_name is not None:
        sub.custom_name = data.custom_name
    if data.fetch_interval is not None:
        sub.fetch_interval = max(data.fetch_interval, 60)
    if data.notify_enabled is not None:
        sub.notify_enabled = data.notify_enabled
    if data.notify_channels is not None:
        sub.notify_channels = data.notify_channels
    if data.dnd_exempt is not None:
        sub.dnd_exempt = data.dnd_exempt

    if data.group_ids is not None:
        groups_result = await db.execute(
            select(Group).where(Group.id.in_(data.group_ids), Group.user_id == user_id)
        )
        sub.groups = list(groups_result.scalars().all())

    if data.tag_ids is not None:
        tags_result = await db.execute(
            select(Tag).where(Tag.id.in_(data.tag_ids), Tag.user_id == user_id)
        )
        sub.tags = list(tags_result.scalars().all())

    await db.commit()

    result = await db.execute(
        select(Subscription)
        .where(Subscription.id == sub.id)
        .options(selectinload(Subscription.source))
    )
    return result.scalar_one()
