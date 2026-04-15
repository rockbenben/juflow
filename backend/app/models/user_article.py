import uuid
from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UserArticle(Base):
    __tablename__ = "user_articles"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    article_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    is_favorited: Mapped[bool] = mapped_column(Boolean, default=False)
    is_read_later: Mapped[bool] = mapped_column(Boolean, default=False)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user = relationship("User", back_populates="user_articles")
    article = relationship("Article", back_populates="user_articles")
