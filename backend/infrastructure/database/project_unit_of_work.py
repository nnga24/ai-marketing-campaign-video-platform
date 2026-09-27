from application.identity.repositories import (
    WorkspaceMembershipRepository,
)
from application.projects.repositories import ProjectRepository
from application.projects.unit_of_work import ProjectUnitOfWork
from application.workspaces.repositories import WorkspaceRepository
from infrastructure.database.repositories.projects import (
    SQLAlchemyProjectRepository,
)
from infrastructure.database.repositories.workspace_memberships import (
    SQLAlchemyWorkspaceMembershipRepository,
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

    @property
    def workspace_memberships(
        self,
    ) -> WorkspaceMembershipRepository:
        session = self._require_session()

        return SQLAlchemyWorkspaceMembershipRepository(
            session,
        )