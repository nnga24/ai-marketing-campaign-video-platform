from uuid import uuid4

import pytest

from application.identity.authentication import (
    AuthenticationFailedError,
    VerifiedExternalIdentity,
    resolve_authenticated_user_id,
)
from application.identity.repositories import (
    ExternalIdentityRepository,
    UserRepository,
)
from modules.identity.models import (
    ExternalIdentity,
    User,
)


class FakeExternalIdentityRepository(
    ExternalIdentityRepository
):
    def __init__(
        self,
        external_identity: ExternalIdentity | None,
    ) -> None:
        self._external_identity = external_identity

    def get_by_issuer_and_subject(
        self,
        *,
        issuer: str,
        subject: str,
    ) -> ExternalIdentity | None:
        return self._external_identity


class FakeUserRepository(UserRepository):
    def __init__(
        self,
        user: User | None,
    ) -> None:
        self._user = user

    def get_by_id(
        self,
        user_id,
    ) -> User | None:
        if (
            self._user is not None
            and self._user.id == user_id
        ):
            return self._user

        return None


def test_resolve_authenticated_user_id_returns_active_user():
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

    result = resolve_authenticated_user_id(
        identity=VerifiedExternalIdentity(
            issuer="https://issuer.example.com",
            subject="subject-123",
        ),
        external_identities=FakeExternalIdentityRepository(
            external_identity,
        ),
        users=FakeUserRepository(user),
    )

    assert result == user_id


def test_resolve_authenticated_user_id_rejects_unlinked_identity():
    with pytest.raises(
        AuthenticationFailedError,
    ):
        resolve_authenticated_user_id(
            identity=VerifiedExternalIdentity(
                issuer="https://issuer.example.com",
                subject="missing-subject",
            ),
            external_identities=FakeExternalIdentityRepository(
                None,
            ),
            users=FakeUserRepository(None),
        )


def test_resolve_authenticated_user_id_rejects_inactive_user():
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
        is_active=False,
    )

    with pytest.raises(
        AuthenticationFailedError,
    ):
        resolve_authenticated_user_id(
            identity=VerifiedExternalIdentity(
                issuer="https://issuer.example.com",
                subject="subject-123",
            ),
            external_identities=FakeExternalIdentityRepository(
                external_identity,
            ),
            users=FakeUserRepository(user),
        )