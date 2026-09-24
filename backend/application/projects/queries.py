from __future__ import annotations

from uuid import UUID

from application.identity.access import (
    WORKSPACE_READ_ROLES,
    require_workspace_access,
)
from application.projects.dto import ProjectView
from application.projects.unit_of_work import ProjectUnitOfWork


class ProjectNotFoundError(LookupError):
    pass


def get_project(
    *,
    project_id: UUID,
    user_id: UUID,
    uow: ProjectUnitOfWork,
) -> ProjectView:
    with uow:
        project = uow.projects.get_by_id(project_id)

        if project is None:
            raise ProjectNotFoundError(
                f"Project '{project_id}' was not found."
            )

        require_workspace_access(
            workspace_id=project.workspace_id,
            user_id=user_id,
            allowed_roles=WORKSPACE_READ_ROLES,
            memberships=uow.workspace_memberships,
        )

        return ProjectView(
            id=project.id,
            workspace_id=project.workspace_id,
            name=project.name,
            slug=project.slug,
            status=project.status,
            created_at=project.created_at,
            updated_at=project.updated_at,
        )