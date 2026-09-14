from uuid import uuid4

import pytest

from application.projects.commands import (
    CreateProjectCommand,
    ProjectSlugConflictError,
    WorkspaceNotFoundError,
    create_project,
)
from application.projects.repositories import ProjectRepository
from application.projects.unit_of_work import ProjectUnitOfWork
from application.workspaces.repositories import WorkspaceRepository
from modules.projects.models import Project
from modules.workspaces.models import Workspace


class FakeProjectRepository(ProjectRepository):
    def __init__(
        self,
        existing_project: Project | None = None,
    ) -> None:
        self.existing_project = existing_project
        self.added_project: Project | None = None

    def get_by_id(
        self,
        project_id,
    ) -> Project | None:
        return None

    def get_by_workspace_and_slug(
        self,
        *,
        workspace_id,
        slug: str,
    ) -> Project | None:
        return self.existing_project

    def add(
        self,
        project: Project,
    ) -> None:
        self.added_project = project


class FakeWorkspaceRepository(WorkspaceRepository):
    def __init__(
        self,
        workspace: Workspace | None,
    ) -> None:
        self.workspace = workspace

    def get_by_id(
        self,
        workspace_id,
    ) -> Workspace | None:
        if (
            self.workspace is not None
            and self.workspace.id == workspace_id
        ):
            return self.workspace

        return None


class FakeProjectUnitOfWork(ProjectUnitOfWork):
    def __init__(
        self,
        *,
        projects: ProjectRepository,
        workspaces: WorkspaceRepository,
    ) -> None:
        self._projects = projects
        self._workspaces = workspaces
        self.committed = False

    def __enter__(self):
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> None:
        pass

    @property
    def projects(self) -> ProjectRepository:
        return self._projects

    @property
    def workspaces(self) -> WorkspaceRepository:
        return self._workspaces

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        pass


def test_create_project_adds_project_and_commits():
    workspace_id = uuid4()
    workspace = Workspace(
        id=workspace_id,
        name="F&B Workspace",
        slug="fb-workspace",
    )

    projects = FakeProjectRepository()
    uow = FakeProjectUnitOfWork(
        projects=projects,
        workspaces=FakeWorkspaceRepository(workspace),
    )

    project_id = create_project(
        command=CreateProjectCommand(
            workspace_id=workspace_id,
            name="Gà Ủ Muối Campaign",
            slug="ga-u-muoi-campaign",
        ),
        uow=uow,
    )

    assert projects.added_project is not None
    assert projects.added_project.id == project_id
    assert projects.added_project.workspace_id == workspace_id
    assert projects.added_project.name == "Gà Ủ Muối Campaign"
    assert projects.added_project.slug == "ga-u-muoi-campaign"
    assert uow.committed is True


def test_create_project_raises_when_workspace_does_not_exist():
    workspace_id = uuid4()

    projects = FakeProjectRepository()
    uow = FakeProjectUnitOfWork(
        projects=projects,
        workspaces=FakeWorkspaceRepository(None),
    )

    with pytest.raises(
        WorkspaceNotFoundError,
        match=str(workspace_id),
    ):
        create_project(
            command=CreateProjectCommand(
                workspace_id=workspace_id,
                name="Campaign",
                slug="campaign",
            ),
            uow=uow,
        )

    assert projects.added_project is None
    assert uow.committed is False


def test_create_project_raises_when_slug_already_exists():
    workspace_id = uuid4()
    workspace = Workspace(
        id=workspace_id,
        name="F&B Workspace",
        slug="fb-workspace",
    )

    existing_project = Project(
        id=uuid4(),
        workspace_id=workspace_id,
        name="Existing Campaign",
        slug="campaign",
    )

    projects = FakeProjectRepository(
        existing_project=existing_project,
    )
    uow = FakeProjectUnitOfWork(
        projects=projects,
        workspaces=FakeWorkspaceRepository(workspace),
    )

    with pytest.raises(
        ProjectSlugConflictError,
        match="campaign",
    ):
        create_project(
            command=CreateProjectCommand(
                workspace_id=workspace_id,
                name="New Campaign",
                slug="campaign",
            ),
            uow=uow,
        )

    assert projects.added_project is None
    assert uow.committed is False