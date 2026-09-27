from uuid import uuid4

import pytest

from application.identity.access import (
    WORKSPACE_READ_ROLES,
    WORKSPACE_WRITE_ROLES,
    WorkspaceAccessDeniedError,
    require_workspace_access,
)
from application.identity.repositories import (
    WorkspaceMembershipRepository,
)
from modules.identity.enums import WorkspaceRole
from modules.identity.models import WorkspaceMembership


class FakeWorkspaceMembershipRepository(
    WorkspaceMembershipRepository
):
    def __init__(
        self,
        membership: WorkspaceMembership | None,
    ) -> None:
        self.membership = membership

    def get_active_membership(
        self,
        *,
        workspace_id,
        user_id,
    ) -> WorkspaceMembership | None:
        return self.membership


def build_membership(
    *,
    workspace_id,
    user_id,
    role: WorkspaceRole,
) -> WorkspaceMembership:
    return WorkspaceMembership(
        id=uuid4(),
        workspace_id=workspace_id,
        user_id=user_id,
        role=role,
        is_active=True,
    )


def test_require_workspace_access_returns_membership_for_allowed_role():
    workspace_id = uuid4()
    user_id = uuid4()

    membership = build_membership(
        workspace_id=workspace_id,
        user_id=user_id,
        role=WorkspaceRole.VIEWER,
    )

    result = require_workspace_access(
        workspace_id=workspace_id,
        user_id=user_id,
        allowed_roles=WORKSPACE_READ_ROLES,
        memberships=FakeWorkspaceMembershipRepository(
            membership,
        ),
    )

    assert result is membership


def test_require_workspace_access_denies_missing_membership():
    workspace_id = uuid4()
    user_id = uuid4()

    with pytest.raises(
        WorkspaceAccessDeniedError,
        match=str(workspace_id),
    ):
        require_workspace_access(
            workspace_id=workspace_id,
            user_id=user_id,
            allowed_roles=WORKSPACE_READ_ROLES,
            memberships=FakeWorkspaceMembershipRepository(
                None,
            ),
        )


def test_require_workspace_access_denies_disallowed_role():
    workspace_id = uuid4()
    user_id = uuid4()

    membership = build_membership(
        workspace_id=workspace_id,
        user_id=user_id,
        role=WorkspaceRole.VIEWER,
    )

    with pytest.raises(WorkspaceAccessDeniedError):
        require_workspace_access(
            workspace_id=workspace_id,
            user_id=user_id,
            allowed_roles=WORKSPACE_WRITE_ROLES,
            memberships=FakeWorkspaceMembershipRepository(
                membership,
            ),
        )