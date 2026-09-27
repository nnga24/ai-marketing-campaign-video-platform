from uuid import UUID

from sqlalchemy.orm import Session

from application.identity.repositories import UserRepository
from modules.identity.models import User


class SQLAlchemyUserRepository(UserRepository):
    def __init__(
        self,
        session: Session,
    ) -> None:
        self._session = session

    def get_by_id(
        self,
        user_id: UUID,
    ) -> User | None:
        return self._session.get(
            User,
            user_id,
        )