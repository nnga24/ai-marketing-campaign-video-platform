from uuid import UUID

from sqlalchemy.orm import Session

from application.workspaces.repositories import WorkspaceRepository
from modules.workspaces.models import Workspace


class SQLAlchemyWorkspaceRepository(WorkspaceRepository):
    def __init__(
        self,
        session: Session,
    ) -> None:
        self._session = session

    def get_by_id(
        self,
        workspace_id: UUID,
    ) -> Workspace | None:
        return self._session.get(
            Workspace,
            workspace_id,
        )