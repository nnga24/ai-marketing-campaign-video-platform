from __future__ import annotations

from uuid import UUID

from application.projects.dto import ProjectView
from application.projects.unit_of_work import ProjectUnitOfWork


class ProjectNotFoundError(LookupError):
    pass


def get_project(
    *,
    project_id: UUID,
    uow: ProjectUnitOfWork,
) -> ProjectView:
    with uow:
        project = uow.projects.get_by_id(project_id)

        if project is None:
            raise ProjectNotFoundError(
                f"Project '{project_id}' was not found."
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