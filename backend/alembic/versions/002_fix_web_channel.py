"""replace stale "web" channel key with the dispatcher's "web_push"

Rows created before the fallback fix stored notify_channels /
notify_defaults as ["web"], which the notifier dispatcher silently
drops. Rewrite them in place so existing installs start receiving again.
Element order is preserved (WITH ORDINALITY) so a rewrite is a pure key
swap, not a reshuffle.

Revision ID: 002
Revises: 001
Create Date: 2026-10-04
"""
from alembic import op

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        UPDATE subscriptions
        SET notify_channels = (
            SELECT jsonb_agg(CASE v WHEN 'web' THEN 'web_push' ELSE v END ORDER BY ord)
            FROM jsonb_array_elements_text(notify_channels) WITH ORDINALITY AS e(v, ord)
        )
        WHERE notify_channels @> '["web"]'::jsonb
    """)
    op.execute("""
        UPDATE users
        SET settings = jsonb_set(
            settings, '{notify_defaults}',
            (SELECT jsonb_agg(CASE v WHEN 'web' THEN 'web_push' ELSE v END ORDER BY ord)
             FROM jsonb_array_elements_text(settings -> 'notify_defaults') WITH ORDINALITY AS e(v, ord))
        )
        WHERE settings ? 'notify_defaults'
          AND settings -> 'notify_defaults' @> '["web"]'::jsonb
    """)


def downgrade() -> None:
    # Intentionally not reversing the key rename: "web" is not a valid channel.
    pass
