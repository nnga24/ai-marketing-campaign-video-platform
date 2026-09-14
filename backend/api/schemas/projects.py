from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from modules.common.enums import EntityStatus


class CreateProjectRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    workspace_id: UUID
    name: str = Field(
        min_length=1,
        max_length=255,
    )
    slug: str = Field(
        min_length=1,
        max_length=120,
    )


class CreateProjectResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID


class ProjectResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID
    workspace_id: UUID
    name: str
    slug: str
    status: EntityStatus
    created_at: datetime
    updated_at: datetime