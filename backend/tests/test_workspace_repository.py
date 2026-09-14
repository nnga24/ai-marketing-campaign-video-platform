from uuid import uuid4
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from infrastructure.database.repositories.workspaces import (
    SQLAlchemyWorkspaceRepository,
)
from modules.workspaces.models import Workspace


def test_workspace_repository_get_by_id():
    session = MagicMock(spec=Session)
    repository = SQLAlchemyWorkspaceRepository(session)

    workspace_id = uuid4()
    workspace = MagicMock(spec=Workspace)
    session.get.return_value = workspace

    result = repository.get_by_id(workspace_id)

    session.get.assert_called_once_with(
        Workspace,
        workspace_id,
    )
    assert result is workspace

    session.commit.assert_not_called()
    session.rollback.assert_not_called()