from __future__ import annotations

from uuid import UUID

from application.identity.repositories import (
    WorkspaceMembershipRepository,
)
from modules.identity.enums import WorkspaceRole
from modules.identity.models import WorkspaceMembership


WORKSPACE_READ_ROLES = frozenset(
    {
        WorkspaceRole.OWNER,
        WorkspaceRole.ADMIN,
        WorkspaceRole.MEMBER,
        WorkspaceRole.VIEWER,
    }
)

WORKSPACE_WRITE_ROLES = frozenset(
    {
        WorkspaceRole.OWNER,
        WorkspaceRole.ADMIN,
        WorkspaceRole.MEMBER,
    }
)


class WorkspaceAccessDeniedError(PermissionError):
    pass


def require_workspace_access(
    *,
    workspace_id: UUID,
    user_id: UUID,
    allowed_roles: frozenset[WorkspaceRole],
    memberships: WorkspaceMembershipRepository,
) -> WorkspaceMembership:
    membership = memberships.get_active_membership(
        workspace_id=workspace_id,
        user_id=user_id,
    )

    if (
        membership is None
        or membership.role not in allowed_roles
    ):
        raise WorkspaceAccessDeniedError(
            "User does not have access to workspace "
            f"'{workspace_id}'."
        )

    return membership