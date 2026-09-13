from __future__ import annotations

from types import TracebackType
from typing import Callable, Self

from sqlalchemy.orm import Session

from application.common.unit_of_work import UnitOfWork
from infrastructure.database.session import SessionLocal


class SQLAlchemyUnitOfWork(UnitOfWork):
    def __init__(
        self,
        session_factory: Callable[[], Session] = SessionLocal,
    ) -> None:
        self._session_factory = session_factory
        self.session: Session | None = None

    def __enter__(self) -> Self:
        if self.session is not None:
            raise RuntimeError(
                "UnitOfWork context is already active."
            )

        self.session = self._session_factory()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self.session is None:
            return

        try:
            self.session.rollback()
        finally:
            self.session.close()
            self.session = None

    def commit(self) -> None:
        self._require_session().commit()

    def rollback(self) -> None:
        self._require_session().rollback()

    def _require_session(self) -> Session:
        if self.session is None:
            raise RuntimeError(
                "UnitOfWork must be used inside a context manager."
            )

        return self.session