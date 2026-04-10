"""Initial migration

Revision ID: 0001
Revises:
Create Date: 2026-04-10

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "organizations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(500), nullable=False, server_default=""),
        sa.Column("short_name", sa.String(200), nullable=False, server_default=""),
        sa.Column("inn", sa.String(20), nullable=False, server_default=""),
        sa.Column("ogrn", sa.String(20), nullable=False, server_default=""),
        sa.Column("legal_address", sa.String(500), nullable=False, server_default=""),
        sa.Column("bank_name", sa.String(300), nullable=False, server_default=""),
        sa.Column("bik", sa.String(20), nullable=False, server_default=""),
        sa.Column("account", sa.String(30), nullable=False, server_default=""),
        sa.Column("corr_account", sa.String(30), nullable=False, server_default=""),
        sa.Column("phone", sa.String(50), nullable=False, server_default=""),
        sa.Column("signer_name", sa.String(200), nullable=False, server_default=""),
        sa.Column("signer_role", sa.String(200), nullable=False, server_default=""),
        sa.Column("logo_path", sa.String(500), nullable=True),
        sa.Column("signature_path", sa.String(500), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.execute("INSERT INTO organizations (id) VALUES (1)")

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(300), nullable=False),
        sa.Column("position", sa.String(200), nullable=True),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("is_admin", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_approved", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )

    op.create_table(
        "recipients",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("default_recipient_id", sa.Integer(), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["default_recipient_id"], ["recipients.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "project_recipients",
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("recipient_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["recipient_id"], ["recipients.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("project_id", "recipient_id"),
    )

    op.create_table(
        "letters",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("number", sa.Integer(), nullable=False),
        sa.Column("letter_date", sa.Date(), nullable=False, server_default=sa.func.current_date()),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("recipient_id", sa.Integer(), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=False),
        sa.Column("subject", sa.String(500), nullable=True),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("docx_path", sa.String(500), nullable=True),
        sa.Column("pdf_path", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("sent_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["recipient_id"], ["recipients.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Sequence for letter numbers
    op.execute("CREATE SEQUENCE IF NOT EXISTS letter_number_seq START 1")


def downgrade() -> None:
    op.drop_table("letters")
    op.drop_table("project_recipients")
    op.drop_table("projects")
    op.drop_table("recipients")
    op.drop_table("users")
    op.drop_table("organizations")
    op.execute("DROP SEQUENCE IF EXISTS letter_number_seq")
