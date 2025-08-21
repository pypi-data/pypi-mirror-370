"""Create resource_docs table.

Revision ID: ddef6e042fbe
Revises:
Create Date: 2025-08-11 12:41:18.606541
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "ddef6e042fbe"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Create the resource_docs table."""
    op.create_table(
        "resource_docs",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("resource_id", sa.Text(), nullable=False),
        sa.Column("docs", postgresql.JSONB(), nullable=False),
        sa.Column("validation_schema", postgresql.JSONB(), nullable=True),
        sa.Column("modified_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["resource_id"], ["resource.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("resource_id"),
    )


def downgrade():
    """Drop the resource_docs table."""
    op.drop_table("resource_docs")
