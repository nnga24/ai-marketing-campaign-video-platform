from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from modules.identity.models import (
    ExternalIdentity,
    User,
    WorkspaceMembership,
)


class UserRepository(ABC):
    @abstractmethod
    def get_by_id(
        self,
        user_id: UUID,
    ) -> User | None:
        raise NotImplementedError


class ExternalIdentityRepository(ABC):
    @abstractmethod
    def get_by_issuer_and_subject(
        self,
        *,
        issuer: str,
        subject: str,
    ) -> ExternalIdentity | None:
        raise NotImplementedError


class WorkspaceMembershipRepository(ABC):
    @abstractmethod
    def get_active_membership(
        self,
        *,
        workspace_id: UUID,
        user_id: UUID,
    ) -> WorkspaceMembership | None:
        raise NotImplementedError