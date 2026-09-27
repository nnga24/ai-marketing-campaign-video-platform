from __future__ import annotations

from abc import ABC, abstractmethod

from application.identity.authentication import (
    VerifiedExternalIdentity,
)


class AccessTokenVerificationError(PermissionError):
    pass


class AccessTokenVerifier(ABC):
    @abstractmethod
    def verify(
        self,
        token: str,
    ) -> VerifiedExternalIdentity:
        raise NotImplementedError