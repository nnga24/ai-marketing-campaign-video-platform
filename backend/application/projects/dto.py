from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from modules.common.enums import EntityStatus


@dataclass(frozen=True, slots=True)
class ProjectView:
    id: UUID
    workspace_id: UUID
    name: str
    slug: str
    status: EntityStatus
    created_at: datetime
    updated_at: datetime