"""Request and response schemas for the project_members module."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.modules.project_members.models import ProjectRole


class MemberAddRequest(BaseModel):
    """Payload for adding a member to a project."""

    user_id: UUID
    role: ProjectRole = ProjectRole.MEMBER


class MemberRoleUpdateRequest(BaseModel):
    """Payload for updating a member's role."""

    role: ProjectRole


class TransferOwnershipRequest(BaseModel):
    """Payload for transferring project ownership."""

    new_owner_id: UUID


class MemberUserInfo(BaseModel):
    """Nested user info inside a member response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str
    email: str


class MemberResponse(BaseModel):
    """Public representation of a project membership."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    user_id: UUID
    user: MemberUserInfo
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
