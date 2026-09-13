from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from infrastructure.database.project_unit_of_work import (
    SQLAlchemyProjectUnitOfWork,
)
from infrastructure.database.repositories.projects import (
    SQLAlchemyProjectRepository,
)


def build_project_uow():
    session = MagicMock(spec=Session)
    session_factory = MagicMock(return_value=session)

    return (
        SQLAlchemyProjectUnitOfWork(
            session_factory=session_factory,
        ),
        session,
        session_factory,
    )


def test_project_unit_of_work_exposes_project_repository():
    uow, session, _ = build_project_uow()

    with uow:
        repository = uow.projects

        assert isinstance(
            repository,
            SQLAlchemyProjectRepository,
        )
        assert repository._session is session


def test_project_unit_of_work_requires_active_context_for_repository():
    uow, _, _ = build_project_uow()

    try:
        uow.projects
    except RuntimeError as exc:
        assert str(exc) == (
            "UnitOfWork must be used inside a context manager."
        )
    else:
        raise AssertionError(
            "Expected RuntimeError outside active context."
        )


def test_project_unit_of_work_closes_session():
    uow, session, session_factory = build_project_uow()

    with uow:
        _ = uow.projects

    session_factory.assert_called_once_with()
    session.rollback.assert_called_once_with()
    session.close.assert_called_once_with()