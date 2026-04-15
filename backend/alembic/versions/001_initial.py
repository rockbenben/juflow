"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-04-15
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- users ---
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("username", sa.String(100), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("avatar_url", sa.String(500)),
        sa.Column("api_key", sa.String(64)),
        sa.Column("settings", JSONB, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_username", "users", ["username"], unique=True)
    op.create_index("ix_users_api_key", "users", ["api_key"], unique=True)

    # --- sources ---
    op.create_table(
        "sources",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("platform", sa.String(50), nullable=False),
        sa.Column("platform_uid", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("avatar_url", sa.String(500)),
        sa.Column("home_url", sa.String(1000), nullable=False),
        sa.Column("adapter_type", sa.String(50), nullable=False),
        sa.Column("adapter_config", JSONB, server_default=sa.text("'{}'::jsonb")),
        sa.Column("last_fetched_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("platform", "platform_uid", name="uq_source_platform_uid"),
    )

    # --- subscriptions ---
    op.create_table(
        "subscriptions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_id", UUID(as_uuid=True), sa.ForeignKey("sources.id", ondelete="CASCADE"), nullable=False),
        sa.Column("fetch_interval", sa.Integer, nullable=False, server_default="300"),
        sa.Column("notify_enabled", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("notify_channels", JSONB, server_default=sa.text("'[\"web\"]'::jsonb")),
        sa.Column("custom_name", sa.String(255)),
        sa.Column("dnd_exempt", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "source_id", name="uq_subscription_user_source"),
    )

    # --- articles ---
    op.create_table(
        "articles",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("source_id", UUID(as_uuid=True), sa.ForeignKey("sources.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(1000), nullable=False),
        sa.Column("summary", sa.Text, server_default=""),
        sa.Column("content", sa.Text),
        sa.Column("url", sa.String(2000), nullable=False),
        sa.Column("cover_image", sa.String(2000)),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("fingerprint", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_articles_fingerprint", "articles", ["fingerprint"], unique=True)
    op.create_index("ix_articles_source_published", "articles", ["source_id", "published_at"])

    # --- user_articles ---
    op.create_table(
        "user_articles",
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("article_id", UUID(as_uuid=True), sa.ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("is_read", sa.Boolean, server_default="false"),
        sa.Column("is_favorited", sa.Boolean, server_default="false"),
        sa.Column("is_read_later", sa.Boolean, server_default="false"),
        sa.Column("read_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_user_articles_user_read", "user_articles", ["user_id", "is_read"])

    # --- groups ---
    op.create_table(
        "groups",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("icon", sa.String(50)),
        sa.Column("sort_order", sa.Integer, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- tags ---
    op.create_table(
        "tags",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("color", sa.String(7)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- subscription_groups (M2M) ---
    op.create_table(
        "subscription_groups",
        sa.Column("subscription_id", UUID(as_uuid=True), sa.ForeignKey("subscriptions.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("group_id", UUID(as_uuid=True), sa.ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True),
    )

    # --- subscription_tags (M2M) ---
    op.create_table(
        "subscription_tags",
        sa.Column("subscription_id", UUID(as_uuid=True), sa.ForeignKey("subscriptions.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("tag_id", UUID(as_uuid=True), sa.ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
    )

    # --- platform_cookies ---
    op.create_table(
        "platform_cookies",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("platform", sa.String(50), nullable=False),
        sa.Column("cookie_encrypted", sa.LargeBinary, nullable=False),
        sa.Column("is_valid", sa.Boolean, server_default="true"),
        sa.Column("last_validated_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "platform", name="uq_cookie_user_platform"),
    )

    # --- push_subscriptions ---
    op.create_table(
        "push_subscriptions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("endpoint", sa.String(1000), nullable=False),
        sa.Column("p256dh", sa.String(200), nullable=False),
        sa.Column("auth", sa.String(200), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- installed_plugins ---
    op.create_table(
        "installed_plugins",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("display_name", sa.String(200), nullable=False),
        sa.Column("version", sa.String(50), nullable=False),
        sa.Column("author", sa.String(200), server_default=""),
        sa.Column("description", sa.Text, server_default=""),
        sa.Column("adapter_class", sa.String(200), nullable=False),
        sa.Column("enabled", sa.Boolean, server_default="true"),
        sa.Column("installed_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- adapter_health_logs ---
    op.create_table(
        "adapter_health_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("source_id", UUID(as_uuid=True), sa.ForeignKey("sources.id", ondelete="CASCADE"), nullable=False),
        sa.Column("adapter_type", sa.String(50), nullable=False),
        sa.Column("success", sa.Boolean, nullable=False),
        sa.Column("error_message", sa.Text),
        sa.Column("duration_ms", sa.Integer, nullable=False),
        sa.Column("articles_count", sa.Integer, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_health_logs_source_created", "adapter_health_logs", ["source_id", "created_at"])


def downgrade() -> None:
    op.drop_table("adapter_health_logs")
    op.drop_table("installed_plugins")
    op.drop_table("push_subscriptions")
    op.drop_table("platform_cookies")
    op.drop_table("subscription_tags")
    op.drop_table("subscription_groups")
    op.drop_table("tags")
    op.drop_table("groups")
    op.drop_table("user_articles")
    op.drop_table("articles")
    op.drop_table("subscriptions")
    op.drop_table("sources")
    op.drop_table("users")
