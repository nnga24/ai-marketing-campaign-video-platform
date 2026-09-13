from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from modules.common.enums import EntityStatus


class ProjectResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID
    workspace_id: UUID
    name: str
    slug: str
    status: EntityStatus
    created_at: datetime
    updated_at: datetime