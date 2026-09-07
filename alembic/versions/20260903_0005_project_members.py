"""Create project_members table and backfill existing owners.

Revision ID: 20260903_0005
Revises: 20260903_0004
Create Date: 2026-09-03 00:00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260903_0005"
down_revision: str | Sequence[str] | None = "20260903_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create the project_members table with role enum and backfill owners."""

    # Create the project_role enum type
    op.execute("CREATE TYPE project_role AS ENUM ('MEMBER', 'ADMIN', 'OWNER')")

    # Create the project_members table
    op.create_table(
        "project_members",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "project_id",
            sa.Uuid(),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "user_id",
            sa.Uuid(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "role",
            sa.Enum("MEMBER", "ADMIN", "OWNER", name="project_role"),
            nullable=False,
            server_default="MEMBER",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # Add unique constraint
    op.create_unique_constraint(
        "uq_project_members", "project_members", ["project_id", "user_id"]
    )

    # Backfill existing project owners as OWNER members
    op.execute(
        """
        INSERT INTO project_members (id, project_id, user_id, role, created_at, updated_at)
        SELECT
            gen_random_uuid(),
            p.id,
            p.owner_id,
            'OWNER'::project_role,
            NOW(),
            NOW()
        FROM projects p
        WHERE NOT EXISTS (
            SELECT 1 FROM project_members pm
            WHERE pm.project_id = p.id AND pm.user_id = p.owner_id
        )
    """
    )


def downgrade() -> None:
    """Drop the project_members table and the project_role enum."""
    op.drop_table("project_members")
    op.execute("DROP TYPE IF EXISTS project_role")