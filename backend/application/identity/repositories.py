from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from modules.identity.models import WorkspaceMembership


class WorkspaceMembershipRepository(ABC):
    @abstractmethod
    def get_active_membership(
        self,
        *,
        workspace_id: UUID,
        user_id: UUID,
    ) -> WorkspaceMembership | None:
        raise NotImplementedError