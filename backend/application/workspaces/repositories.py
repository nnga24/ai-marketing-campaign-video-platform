from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from modules.workspaces.models import Workspace


class WorkspaceRepository(ABC):
    @abstractmethod
    def get_by_id(
        self,
        workspace_id: UUID,
    ) -> Workspace | None:
        raise NotImplementedError