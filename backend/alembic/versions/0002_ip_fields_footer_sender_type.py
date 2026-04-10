"""Add IP fields, footer_banner, sender_type

Revision ID: 0002
Revises: 0001
Create Date: 2026-04-10
"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Organization: IP fields + footer_banner
    op.add_column("organizations", sa.Column("ip_full_name", sa.String(300), nullable=False, server_default=""))
    op.add_column("organizations", sa.Column("ip_inn", sa.String(20), nullable=False, server_default=""))
    op.add_column("organizations", sa.Column("ip_ogrnip", sa.String(20), nullable=False, server_default=""))
    op.add_column("organizations", sa.Column("ip_legal_address", sa.String(500), nullable=False, server_default=""))
    op.add_column("organizations", sa.Column("ip_bank_name", sa.String(300), nullable=False, server_default=""))
    op.add_column("organizations", sa.Column("ip_bik", sa.String(20), nullable=False, server_default=""))
    op.add_column("organizations", sa.Column("ip_account", sa.String(30), nullable=False, server_default=""))
    op.add_column("organizations", sa.Column("ip_corr_account", sa.String(30), nullable=False, server_default=""))
    op.add_column("organizations", sa.Column("ip_phone", sa.String(50), nullable=False, server_default=""))
    op.add_column("organizations", sa.Column("ip_signer_name", sa.String(200), nullable=False, server_default=""))
    op.add_column("organizations", sa.Column("ip_signer_role", sa.String(200), nullable=False, server_default=""))
    op.add_column("organizations", sa.Column("footer_banner_path", sa.String(500), nullable=True))

    # Letter: sender_type
    op.add_column("letters", sa.Column("sender_type", sa.String(10), nullable=False, server_default="ooo"))


def downgrade() -> None:
    op.drop_column("letters", "sender_type")
    for col in ["ip_full_name", "ip_inn", "ip_ogrnip", "ip_legal_address", "ip_bank_name",
                "ip_bik", "ip_account", "ip_corr_account", "ip_phone", "ip_signer_name",
                "ip_signer_role", "footer_banner_path"]:
        op.drop_column("organizations", col)
