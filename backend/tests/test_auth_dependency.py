import pytest
from fastapi import HTTPException

from api.dependencies.auth import get_current_user_id


def test_get_current_user_id_fails_closed_without_authentication():
    with pytest.raises(HTTPException) as exc_info:
        get_current_user_id()

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Authentication is required."