from __future__ import annotations

from collections.abc import Sequence

import jwt
from jwt import PyJWKClient
from jwt.exceptions import PyJWTError

from application.identity.authentication import (
    VerifiedExternalIdentity,
)
from application.identity.token_verifier import (
    AccessTokenVerificationError,
    AccessTokenVerifier,
)


class JWTAccessTokenVerifier(AccessTokenVerifier):
    def __init__(
        self,
        *,
        issuer: str,
        audience: str,
        jwks_url: str,
        algorithms: Sequence[str],
    ) -> None:
        if not issuer:
            raise ValueError("JWT issuer is required.")

        if not audience:
            raise ValueError("JWT audience is required.")

        if not jwks_url:
            raise ValueError("JWKS URL is required.")

        if not algorithms:
            raise ValueError(
                "At least one JWT algorithm is required."
            )

        self._issuer = issuer
        self._audience = audience
        self._algorithms = tuple(algorithms)
        self._jwk_client = PyJWKClient(jwks_url)

    def verify(
        self,
        token: str,
    ) -> VerifiedExternalIdentity:
        if not token.strip():
            raise AccessTokenVerificationError(
                "Access token is required."
            )

        try:
            signing_key = (
                self._jwk_client.get_signing_key_from_jwt(
                    token
                )
            )

            claims = jwt.decode(
                token,
                signing_key.key,
                algorithms=list(self._algorithms),
                audience=self._audience,
                issuer=self._issuer,
                options={
                    "require": [
                        "exp",
                        "iss",
                        "sub",
                    ],
                },
            )
        except PyJWTError as exc:
            raise AccessTokenVerificationError(
                "Access token verification failed."
            ) from exc

        issuer = claims.get("iss")
        subject = claims.get("sub")

        if (
            not isinstance(issuer, str)
            or not issuer
            or not isinstance(subject, str)
            or not subject
        ):
            raise AccessTokenVerificationError(
                "Access token identity claims are invalid."
            )

        return VerifiedExternalIdentity(
            issuer=issuer,
            subject=subject,
        )