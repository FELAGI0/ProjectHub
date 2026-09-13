"""Request and response schemas for the project_members module."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.modules.project_members.models import ProjectRole


class MemberAddRequest(BaseModel):
    """Payload for adding a member to a project."""

    model_config = ConfigDict(str_strip_whitespace=True)

    user_id: UUID
    role: ProjectRole = ProjectRole.MEMBER


class MemberRoleUpdateRequest(BaseModel):
    """Payload for updating a member's role."""

    role: ProjectRole


class MemberResponse(BaseModel):
    """Public representation of a project membership."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    user_id: UUID
    role: ProjectRole
    created_at: datetime
    updated_at: datetime


class PaginatedMembersResponse(BaseModel):
    """Paginated list of project members."""

    items: list[MemberResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
