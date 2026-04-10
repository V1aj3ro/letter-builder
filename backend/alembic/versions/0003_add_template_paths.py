"""Add template_ooo_path and template_ip_path to organizations

Revision ID: 0003
Revises: 0002
Create Date: 2026-04-10
"""
from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("organizations", sa.Column("template_ooo_path", sa.String(500), nullable=True))
    op.add_column("organizations", sa.Column("template_ip_path",  sa.String(500), nullable=True))


def downgrade() -> None:
    op.drop_column("organizations", "template_ip_path")
    op.drop_column("organizations", "template_ooo_path")
