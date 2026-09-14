from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from api.schemas.projects import (
    CreateProjectRequest,
    CreateProjectResponse,
    ProjectResponse,
)
from application.projects.commands import (
    CreateProjectCommand,
    ProjectSlugConflictError,
    WorkspaceNotFoundError,
    create_project,
)
from application.projects.queries import (
    ProjectNotFoundError,
    get_project,
)
from application.projects.unit_of_work import ProjectUnitOfWork
from infrastructure.database.project_unit_of_work import (
    SQLAlchemyProjectUnitOfWork,
)


router = APIRouter()


def get_project_unit_of_work() -> ProjectUnitOfWork:
    return SQLAlchemyProjectUnitOfWork()

@router.post(
    "/",
    response_model=CreateProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_project_route(
    request: CreateProjectRequest,
    uow: ProjectUnitOfWork = Depends(
        get_project_unit_of_work,
    ),
) -> CreateProjectResponse:
    try:
        project_id = create_project(
            command=CreateProjectCommand(
                workspace_id=request.workspace_id,
                name=request.name,
                slug=request.slug,
            ),
            uow=uow,
        )
    except WorkspaceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ProjectSlugConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return CreateProjectResponse(
        id=project_id,
    )

@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
)
def read_project(
    project_id: UUID,
    uow: ProjectUnitOfWork = Depends(
        get_project_unit_of_work,
    ),
) -> ProjectResponse:
    try:
        project = get_project(
            project_id=project_id,
            uow=uow,
        )
    except ProjectNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return ProjectResponse(
        id=project.id,
        workspace_id=project.workspace_id,
        name=project.name,
        slug=project.slug,
        status=project.status,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )