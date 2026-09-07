"""SQLAlchemy model for the project_members table."""

import enum
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.modules.users.models import User

if TYPE_CHECKING:
    from app.modules.projects.models import Project


class ProjectRole(enum.StrEnum):
    """Allowed roles within a project."""

    MEMBER = "MEMBER"
    ADMIN = "ADMIN"
    OWNER = "OWNER"

    @property
    def level(self) -> int:
        """Return a numeric level for hierarchy comparisons."""
        return {"MEMBER": 1, "ADMIN": 2, "OWNER": 3}[self.value]


class ProjectMember(Base):
    """A user's membership in a project with an assigned role."""

    __tablename__ = "project_members"

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid4
    )
    project_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[ProjectRole] = mapped_column(
        Enum(ProjectRole, name="project_role", create_constraint=True),
        nullable=False,
        default=ProjectRole.MEMBER,
        server_default=ProjectRole.MEMBER.value,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped[User] = relationship(back_populates="project_members")
    project: Mapped["Project"] = relationship(back_populates="members")

    __table_args__ = (
        UniqueConstraint("project_id", "user_id", name="uq_project_members"),
    )