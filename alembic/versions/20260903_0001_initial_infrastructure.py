"""Create initial migration baseline.

Revision ID: 20260903_0001
Revises:
Create Date: 2026-09-03 00:00:00
"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "20260903_0001"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create the migration baseline without application tables."""


def downgrade() -> None:
    """Revert the migration baseline without application tables."""
