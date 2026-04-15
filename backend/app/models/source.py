import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform: Mapped[str] = mapped_column(String(50))
    platform_uid: Mapped[str] = mapped_column(String(255))
    display_name: Mapped[str] = mapped_column(String(255))
    avatar_url: Mapped[str | None] = mapped_column(String(500))
    home_url: Mapped[str] = mapped_column(String(1000))
    adapter_type: Mapped[str] = mapped_column(String(50))
    adapter_config: Mapped[dict] = mapped_column(JSONB, default=dict)
    last_fetched_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    subscriptions = relationship("Subscription", back_populates="source")
    articles = relationship("Article", back_populates="source", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("platform", "platform_uid", name="uq_source_platform_uid"),)
