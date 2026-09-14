from uuid import uuid4
from unittest.mock import MagicMock
from sqlalchemy import select
from sqlalchemy.orm import Session

from infrastructure.database.repositories.projects import (
    SQLAlchemyProjectRepository,
)
from modules.projects.models import Project


def test_project_repository_get_by_id():
    session = MagicMock(spec=Session)
    repository = SQLAlchemyProjectRepository(session)

    project_id = uuid4()
    project = MagicMock(spec=Project)
    session.get.return_value = project

    result = repository.get_by_id(project_id)

    session.get.assert_called_once_with(Project, project_id)
    assert result is project


def test_project_repository_add():
    session = MagicMock(spec=Session)
    repository = SQLAlchemyProjectRepository(session)

    project = MagicMock(spec=Project)

    repository.add(project)

    session.add.assert_called_once_with(project)
    session.commit.assert_not_called()
    session.rollback.assert_not_called()

def test_project_repository_get_by_workspace_and_slug():
    session = MagicMock(spec=Session)
    repository = SQLAlchemyProjectRepository(session)

    workspace_id = uuid4()
    project = MagicMock(spec=Project)
    session.scalar.return_value = project

    result = repository.get_by_workspace_and_slug(
        workspace_id=workspace_id,
        slug="fb-marketing",
    )

    session.scalar.assert_called_once()

    statement = session.scalar.call_args.args[0]

    assert str(statement) == str(
        select(Project).where(
            Project.workspace_id == workspace_id,
            Project.slug == "fb-marketing",
        )
    )

    assert result is project
    session.commit.assert_not_called()
    session.rollback.assert_not_called()