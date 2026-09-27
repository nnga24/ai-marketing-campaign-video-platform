from unittest.mock import Mock
from uuid import uuid4

from infrastructure.database.repositories.users import (
    SQLAlchemyUserRepository,
)
from modules.identity.models import User


def test_get_by_id_uses_session_get():
    user_id = uuid4()
    expected_user = Mock(spec=User)

    session = Mock()
    session.get.return_value = expected_user

    repository = SQLAlchemyUserRepository(session)

    result = repository.get_by_id(user_id)

    session.get.assert_called_once_with(
        User,
        user_id,
    )
    assert result is expected_user