import uuid
from datetime import datetime

from sqlalchemy import String, Boolean, ForeignKey, DateTime, LargeBinary, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class PlatformCookie(Base):
    __tablename__ = "platform_cookies"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    platform: Mapped[str] = mapped_column(String(50))
    cookie_encrypted: Mapped[bytes] = mapped_column(LargeBinary)
    is_valid: Mapped[bool] = mapped_column(Boolean, default=True)
    last_validated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (UniqueConstraint("user_id", "platform", name="uq_cookie_user_platform"),)
