from datetime import datetime, timezone
from uuid import uuid4

import pytest
from application.workspaces.repositories import WorkspaceRepository
from application.projects.dto import ProjectView
from application.projects.queries import (
    ProjectNotFoundError,
    get_project,
)
from application.projects.repositories import ProjectRepository
from application.projects.unit_of_work import ProjectUnitOfWork
from modules.common.enums import EntityStatus
from modules.projects.models import Project


class FakeProjectRepository(ProjectRepository):
    def __init__(
        self,
        project: Project | None,
    ) -> None:
        self._project = project

    def get_by_id(
        self,
        project_id,
    ) -> Project | None:
        if (
            self._project is not None
            and self._project.id == project_id
        ):
            return self._project

        return None
    def get_by_workspace_and_slug(
        self,
        *,
        workspace_id,
        slug: str,
    ) -> Project | None:
        raise NotImplementedError
    
    def add(
        self,
        project: Project,
    ) -> None:
        raise NotImplementedError


class FakeProjectUnitOfWork(ProjectUnitOfWork):
    def __init__(
        self,
        repository: ProjectRepository,
    ) -> None:
        self._repository = repository
        self.entered = False
        self.exited = False
        self.committed = False
        self.rolled_back = False

    def __enter__(self):
        self.entered = True
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> None:
        self.exited = True

    @property
    def projects(self) -> ProjectRepository:
        if not self.entered:
            raise RuntimeError(
                "UnitOfWork is not active."
            )

        return self._repository

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True
    @property
    def workspaces(self) -> WorkspaceRepository:
        raise NotImplementedError


def test_get_project_returns_application_view():
    project_id = uuid4()
    workspace_id = uuid4()
    now = datetime.now(timezone.utc)

    project = Project(
        id=project_id,
        workspace_id=workspace_id,
        name="F&B Marketing",
        slug="fb-marketing",
        status=EntityStatus.ACTIVE,
        created_at=now,
        updated_at=now,
    )

    uow = FakeProjectUnitOfWork(
        FakeProjectRepository(project),
    )

    result = get_project(
        project_id=project_id,
        uow=uow,
    )

    assert isinstance(result, ProjectView)
    assert result.id == project_id
    assert result.workspace_id == workspace_id
    assert result.name == "F&B Marketing"
    assert result.slug == "fb-marketing"
    assert result.status == EntityStatus.ACTIVE
    assert result.created_at == now
    assert result.updated_at == now

    assert uow.entered is True
    assert uow.exited is True
    assert uow.committed is False


def test_get_project_raises_when_project_does_not_exist():
    project_id = uuid4()

    uow = FakeProjectUnitOfWork(
        FakeProjectRepository(None),
    )

    with pytest.raises(
        ProjectNotFoundError,
        match=str(project_id),
    ):
        get_project(
            project_id=project_id,
            uow=uow,
        )

    assert uow.entered is True
    assert uow.exited is True
    assert uow.committed is False