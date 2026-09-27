from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from application.identity.repositories import (
    ExternalIdentityRepository,
    UserRepository,
)


class AuthenticationFailedError(PermissionError):
    pass


@dataclass(frozen=True, slots=True)
class VerifiedExternalIdentity:
    issuer: str
    subject: str


def resolve_authenticated_user_id(
    *,
    identity: VerifiedExternalIdentity,
    external_identities: ExternalIdentityRepository,
    users: UserRepository,
) -> UUID:
    external_identity = (
        external_identities.get_by_issuer_and_subject(
            issuer=identity.issuer,
            subject=identity.subject,
        )
    )

    if external_identity is None:
        raise AuthenticationFailedError(
            "External identity is not linked to a user."
        )

    user = users.get_by_id(
        external_identity.user_id,
    )

    if user is None or not user.is_active:
        raise AuthenticationFailedError(
            "Authenticated user is not active."
        )

    return user.id