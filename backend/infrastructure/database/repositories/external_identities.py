from sqlalchemy import select
from sqlalchemy.orm import Session

from application.identity.repositories import (
    ExternalIdentityRepository,
)
from modules.identity.models import ExternalIdentity


class SQLAlchemyExternalIdentityRepository(
    ExternalIdentityRepository
):
    def __init__(
        self,
        session: Session,
    ) -> None:
        self._session = session

    def get_by_issuer_and_subject(
        self,
        *,
        issuer: str,
        subject: str,
    ) -> ExternalIdentity | None:
        statement = select(
            ExternalIdentity
        ).where(
            ExternalIdentity.issuer == issuer,
            ExternalIdentity.subject == subject,
        )

        return self._session.scalar(statement)