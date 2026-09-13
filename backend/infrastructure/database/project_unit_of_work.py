from application.projects.repositories import ProjectRepository
from application.projects.unit_of_work import ProjectUnitOfWork
from application.workspaces.repositories import WorkspaceRepository
from infrastructure.database.repositories.projects import (
    SQLAlchemyProjectRepository,
)
from infrastructure.database.repositories.workspaces import (
    SQLAlchemyWorkspaceRepository,
)
from infrastructure.database.unit_of_work import SQLAlchemyUnitOfWork


class SQLAlchemyProjectUnitOfWork(
    SQLAlchemyUnitOfWork,
    ProjectUnitOfWork,
):
    @property
    def projects(self) -> ProjectRepository:
        session = self._require_session()

        return SQLAlchemyProjectRepository(session)

    @property
    def workspaces(self) -> WorkspaceRepository:
        session = self._require_session()

        return SQLAlchemyWorkspaceRepository(session)