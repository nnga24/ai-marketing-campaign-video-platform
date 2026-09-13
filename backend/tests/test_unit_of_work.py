from unittest.mock import MagicMock

import pytest
from sqlalchemy.orm import Session

from infrastructure.database.unit_of_work import SQLAlchemyUnitOfWork


def build_uow():
    session = MagicMock(spec=Session)
    session_factory = MagicMock(return_value=session)

    return SQLAlchemyUnitOfWork(
        session_factory=session_factory,
    ), session, session_factory


def test_unit_of_work_opens_and_closes_session():
    uow, session, session_factory = build_uow()

    with uow as active_uow:
        assert active_uow is uow
        assert uow.session is session
        session_factory.assert_called_once_with()

    session.rollback.assert_called_once_with()
    session.close.assert_called_once_with()
    assert uow.session is None


def test_unit_of_work_commit_delegates_to_session():
    uow, session, _ = build_uow()

    with uow:
        uow.commit()

    session.commit.assert_called_once_with()


def test_unit_of_work_rollback_delegates_to_session():
    uow, session, _ = build_uow()

    with uow:
        uow.rollback()

    assert session.rollback.call_count == 2


def test_unit_of_work_requires_active_context_for_commit():
    uow, _, _ = build_uow()

    with pytest.raises(
        RuntimeError,
        match="UnitOfWork must be used inside a context manager.",
    ):
        uow.commit()


def test_unit_of_work_requires_active_context_for_rollback():
    uow, _, _ = build_uow()

    with pytest.raises(
        RuntimeError,
        match="UnitOfWork must be used inside a context manager.",
    ):
        uow.rollback()


def test_unit_of_work_rejects_nested_active_context():
    uow, _, _ = build_uow()

    with uow:
        with pytest.raises(
            RuntimeError,
            match="UnitOfWork context is already active.",
        ):
            uow.__enter__()