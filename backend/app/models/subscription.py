import uuid
from datetime import datetime

from sqlalchemy import String, Integer, Boolean, ForeignKey, UniqueConstraint, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    source_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sources.id", ondelete="CASCADE"))
    fetch_interval: Mapped[int] = mapped_column(Integer, default=300)
    notify_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_channels: Mapped[list] = mapped_column(JSONB, default=lambda: ["web"])
    custom_name: Mapped[str | None] = mapped_column(String(255))
    dnd_exempt: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="subscriptions")
    source = relationship("Source", back_populates="subscriptions")
    groups = relationship("Group", secondary="subscription_groups", back_populates="subscriptions")
    tags = relationship("Tag", secondary="subscription_tags", back_populates="subscriptions")

    __table_args__ = (UniqueConstraint("user_id", "source_id", name="uq_subscription_user_source"),)
