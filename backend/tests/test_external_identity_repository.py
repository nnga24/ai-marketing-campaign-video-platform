from sqlalchemy.dialects import postgresql

from infrastructure.database.repositories.external_identities import (
    SQLAlchemyExternalIdentityRepository,
)
from modules.identity.models import ExternalIdentity


class CapturingSession:
    def __init__(self) -> None:
        self.statement = None

    def scalar(self, statement):
        self.statement = statement
        return None


def test_get_by_issuer_and_subject_filters_identity_key():
    session = CapturingSession()
    repository = SQLAlchemyExternalIdentityRepository(
        session,
    )

    repository.get_by_issuer_and_subject(
        issuer="https://issuer.example.com",
        subject="user-123",
    )

    compiled = session.statement.compile(
        dialect=postgresql.dialect(),
        compile_kwargs={
            "literal_binds": True,
        },
    )

    sql = str(compiled)

    assert "external_identities.issuer" in sql
    assert "external_identities.subject" in sql
    assert "https://issuer.example.com" in sql
    assert "user-123" in sql