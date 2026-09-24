from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid4

from application.projects.unit_of_work import ProjectUnitOfWork
from modules.projects.models import Project
from application.identity.access import (
    WORKSPACE_WRITE_ROLES,
    require_workspace_access,
)

class WorkspaceNotFoundError(LookupError):
    pass


class ProjectSlugConflictError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class CreateProjectCommand:
    workspace_id: UUID
    user_id: UUID
    name: str
    slug: str


def create_project(
    *,
    command: CreateProjectCommand,
    uow: ProjectUnitOfWork,
) -> UUID:
    with uow:
        workspace = uow.workspaces.get_by_id(
            command.workspace_id,
        )

        if workspace is None:
            raise WorkspaceNotFoundError(
                f"Workspace '{command.workspace_id}' was not found."
            )
        
        require_workspace_access(
            workspace_id=command.workspace_id,
            user_id=command.user_id,
            allowed_roles=WORKSPACE_WRITE_ROLES,
            memberships=uow.workspace_memberships,
        )
        existing_project = (
            uow.projects.get_by_workspace_and_slug(
                workspace_id=command.workspace_id,
                slug=command.slug,
            )
        )

        if existing_project is not None:
            raise ProjectSlugConflictError(
                "A project with slug "
                f"'{command.slug}' already exists "
                f"in workspace '{command.workspace_id}'."
            )

        project = Project(
            id=uuid4(),
            workspace_id=command.workspace_id,
            name=command.name,
            slug=command.slug,
        )

        uow.projects.add(project)
        uow.commit()

        return project.id