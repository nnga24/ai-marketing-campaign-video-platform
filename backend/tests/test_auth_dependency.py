from uuid import uuid4

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from api.dependencies.auth import (
    get_bearer_token,
    get_current_user_id,
)
from application.identity.authentication import (
    VerifiedExternalIdentity,
)
from application.identity.token_verifier import (
    AccessTokenVerificationError,
)
from modules.identity.models import (
    ExternalIdentity,
    User,
)


class FakeVerifier:
    def verify(
        self,
        token: str,
    ) -> VerifiedExternalIdentity:
        assert token == "signed-token"

        return VerifiedExternalIdentity(
            issuer="https://issuer.example.com",
            subject="subject-123",
        )


class RejectingVerifier:
    def verify(
        self,
        token: str,
    ) -> VerifiedExternalIdentity:
        raise AccessTokenVerificationError(
            "Invalid token."
        )


class FakeSession:
    def __init__(
        self,
        *,
        external_identity: ExternalIdentity,
        user: User,
    ) -> None:
        self._external_identity = external_identity
        self._user = user

    def scalar(self, statement):
        return self._external_identity

    def get(
        self,
        model,
        identifier,
    ):
        assert model is User
        assert identifier == self._user.id

        return self._user

class UnlinkedIdentitySession:
    def scalar(self, statement):
        return None

def test_get_bearer_token_fails_closed_without_authentication():
    with pytest.raises(HTTPException) as exc_info:
        get_bearer_token(
            credentials=None,
        )

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Authentication is required."
    assert exc_info.value.headers == {
        "WWW-Authenticate": "Bearer",
    }


def test_get_bearer_token_returns_credentials():
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="signed-token",
    )

    result = get_bearer_token(
        credentials=credentials,
    )

    assert result == "signed-token"


def test_get_current_user_id_resolves_valid_bearer_token():
    user_id = uuid4()

    external_identity = ExternalIdentity(
        id=uuid4(),
        user_id=user_id,
        issuer="https://issuer.example.com",
        subject="subject-123",
    )

    user = User(
        id=user_id,
        email="user@example.com",
        is_active=True,
    )

    result = get_current_user_id(
        token="signed-token",
        db=FakeSession(
            external_identity=external_identity,
            user=user,
        ),
        verifier=FakeVerifier(),
    )

    assert result == user_id


def test_get_current_user_id_maps_invalid_token_to_http_401():
    with pytest.raises(HTTPException) as exc_info:
        get_current_user_id(
            token="invalid-token",
            db=object(),
            verifier=RejectingVerifier(),
        )

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Authentication failed."
    assert exc_info.value.headers == {
        "WWW-Authenticate": "Bearer",
    }


def test_get_current_user_id_maps_unlinked_identity_to_http_401():
    with pytest.raises(HTTPException) as exc_info:
        get_current_user_id(
            token="signed-token",
            db=UnlinkedIdentitySession(),
            verifier=FakeVerifier(),
        )

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Authentication failed."
    assert exc_info.value.headers == {
        "WWW-Authenticate": "Bearer",
    }