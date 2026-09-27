from types import SimpleNamespace

import jwt
import pytest

from application.identity.token_verifier import (
    AccessTokenVerificationError,
)
from infrastructure.auth.jwt_verifier import (
    JWTAccessTokenVerifier,
)


class FakeJWKClient:
    def get_signing_key_from_jwt(
        self,
        token: str,
    ):
        assert token == "signed-token"

        return SimpleNamespace(
            key="public-key",
        )


def test_verify_returns_verified_external_identity(
    monkeypatch: pytest.MonkeyPatch,
):
    verifier = JWTAccessTokenVerifier(
        issuer="https://issuer.example.com",
        audience="marketing-api",
        jwks_url="https://issuer.example.com/jwks.json",
        algorithms=("RS256",),
    )

    verifier._jwk_client = FakeJWKClient()

    def fake_decode(
        token,
        key,
        *,
        algorithms,
        audience,
        issuer,
        options,
    ):
        assert token == "signed-token"
        assert key == "public-key"
        assert algorithms == ["RS256"]
        assert audience == "marketing-api"
        assert issuer == "https://issuer.example.com"
        assert options == {
            "require": [
                "exp",
                "iss",
                "sub",
            ],
        }

        return {
            "iss": "https://issuer.example.com",
            "sub": "user-123",
            "aud": "marketing-api",
            "exp": 9999999999,
        }

    monkeypatch.setattr(
        "infrastructure.auth.jwt_verifier.jwt.decode",
        fake_decode,
    )

    identity = verifier.verify("signed-token")

    assert identity.issuer == "https://issuer.example.com"
    assert identity.subject == "user-123"


def test_verify_rejects_invalid_token(
    monkeypatch: pytest.MonkeyPatch,
):
    verifier = JWTAccessTokenVerifier(
        issuer="https://issuer.example.com",
        audience="marketing-api",
        jwks_url="https://issuer.example.com/jwks.json",
        algorithms=("RS256",),
    )

    verifier._jwk_client = FakeJWKClient()

    def fake_decode(*args, **kwargs):
        raise jwt.InvalidTokenError(
            "Invalid token."
        )

    monkeypatch.setattr(
        "infrastructure.auth.jwt_verifier.jwt.decode",
        fake_decode,
    )

    with pytest.raises(
        AccessTokenVerificationError,
    ):
        verifier.verify("signed-token")


def test_verify_rejects_blank_token():
    verifier = JWTAccessTokenVerifier(
        issuer="https://issuer.example.com",
        audience="marketing-api",
        jwks_url="https://issuer.example.com/jwks.json",
        algorithms=("RS256",),
    )

    with pytest.raises(
        AccessTokenVerificationError,
        match="required",
    ):
        verifier.verify("   ")