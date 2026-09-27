from unittest.mock import MagicMock
from uuid import uuid4

from sqlalchemy.orm import Session

from infrastructure.database.repositories.workspace_memberships import (
    SQLAlchemyWorkspaceMembershipRepository,
)
from modules.identity.models import WorkspaceMembership


def test_get_active_workspace_membership():
    session = MagicMock(spec=Session)
    repository = SQLAlchemyWorkspaceMembershipRepository(
        session,
    )

    workspace_id = uuid4()
    user_id = uuid4()
    membership = MagicMock(spec=WorkspaceMembership)

    session.scalar.return_value = membership

    result = repository.get_active_membership(
        workspace_id=workspace_id,
        user_id=user_id,
    )

    statement = session.scalar.call_args.args[0]
    statement_sql = str(statement)

    assert result is membership
    assert "workspace_memberships.workspace_id" in statement_sql
    assert "workspace_memberships.user_id" in statement_sql
    assert "workspace_memberships.is_active IS true" in statement_sql

    session.scalar.assert_called_once()
    session.commit.assert_not_called()
    session.rollback.assert_not_called()