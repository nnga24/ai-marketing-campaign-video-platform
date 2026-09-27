from uuid import UUID

from fastapi import (
    Depends,
    HTTPException,
    Security,
    status,
)
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlalchemy.orm import Session

from application.identity.authentication import (
    AuthenticationFailedError,
    resolve_authenticated_user_id,
)
from application.identity.token_verifier import (
    AccessTokenVerificationError,
    AccessTokenVerifier,
)
from core.config import settings
from infrastructure.auth.jwt_verifier import (
    JWTAccessTokenVerifier,
)
from infrastructure.database.repositories.external_identities import (
    SQLAlchemyExternalIdentityRepository,
)
from infrastructure.database.repositories.users import (
    SQLAlchemyUserRepository,
)
from infrastructure.database.session import get_db


bearer_scheme = HTTPBearer(
    auto_error=False,
)


def get_access_token_verifier() -> AccessTokenVerifier:
    algorithms = tuple(
        algorithm.strip()
        for algorithm in settings.AUTH_JWT_ALGORITHMS.split(",")
        if algorithm.strip()
    )

    return JWTAccessTokenVerifier(
        issuer=settings.AUTH_JWT_ISSUER,
        audience=settings.AUTH_JWT_AUDIENCE,
        jwks_url=settings.AUTH_JWKS_URL,
        algorithms=algorithms,
    )


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials | None = Security(
        bearer_scheme,
    ),
    db: Session = Depends(get_db),
    verifier: AccessTokenVerifier = Depends(
        get_access_token_verifier,
    ),
) -> UUID:
    if (
        credentials is None
        or credentials.scheme.lower() != "bearer"
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication is required.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    try:
        identity = verifier.verify(
            credentials.credentials,
        )

        return resolve_authenticated_user_id(
            identity=identity,
            external_identities=(
                SQLAlchemyExternalIdentityRepository(db)
            ),
            users=SQLAlchemyUserRepository(db),
        )
    except (
        AccessTokenVerificationError,
        AuthenticationFailedError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        ) from exc