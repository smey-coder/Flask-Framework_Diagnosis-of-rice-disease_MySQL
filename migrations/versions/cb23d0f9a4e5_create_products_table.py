"""Create products table

Revision ID: cb23d0f9a4e5
Revises:
Create Date: 2026-11-19 00:28:30.233944

"""
from alembic import op
import sqlalchemy as sa


revision = "cb23d0f9a4e5"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("qty", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("products")
