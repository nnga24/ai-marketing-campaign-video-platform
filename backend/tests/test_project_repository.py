from uuid import uuid4
from unittest.mock import MagicMock

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