from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from application.projects.repositories import ProjectRepository
from modules.projects.models import Project


class SQLAlchemyProjectRepository(ProjectRepository):
    def __init__(
        self,
        session: Session,
    ) -> None:
        self._session = session

    def get_by_id(
        self,
        project_id: UUID,
    ) -> Project | None:
        return self._session.get(
            Project,
            project_id,
        )

    def get_by_workspace_and_slug(
        self,
        *,
        workspace_id: UUID,
        slug: str,
    ) -> Project | None:
        statement = select(Project).where(
            Project.workspace_id == workspace_id,
            Project.slug == slug,
        )

        return self._session.scalar(statement)

    def add(
        self,
        project: Project,
    ) -> None:
        self._session.add(project)