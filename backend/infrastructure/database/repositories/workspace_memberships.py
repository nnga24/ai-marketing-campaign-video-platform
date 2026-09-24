from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from application.identity.repositories import (
    WorkspaceMembershipRepository,
)
from modules.identity.models import WorkspaceMembership


class SQLAlchemyWorkspaceMembershipRepository(
    WorkspaceMembershipRepository
):
    def __init__(
        self,
        session: Session,
    ) -> None:
        self._session = session

    def get_active_membership(
        self,
        *,
        workspace_id: UUID,
        user_id: UUID,
    ) -> WorkspaceMembership | None:
        statement = select(
            WorkspaceMembership
        ).where(
            WorkspaceMembership.workspace_id == workspace_id,
            WorkspaceMembership.user_id == user_id,
            WorkspaceMembership.is_active.is_(True),
        )

        return self._session.scalar(statement)