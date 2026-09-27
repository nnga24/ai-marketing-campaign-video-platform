from sqlalchemy import UniqueConstraint

from modules.identity.models import ExternalIdentity


def test_external_identity_has_provider_neutral_identity_key():
    table = ExternalIdentity.__table__

    assert table.name == "external_identities"

    assert {
        "id",
        "user_id",
        "issuer",
        "subject",
        "created_at",
        "updated_at",
    }.issubset(table.columns.keys())

    unique_constraints = {
        tuple(constraint.columns.keys())
        for constraint in table.constraints
        if isinstance(constraint, UniqueConstraint)
    }

    assert (
        "issuer",
        "subject",
    ) in unique_constraints


def test_external_identity_references_internal_user():
    user_id_foreign_keys = {
        foreign_key.target_fullname
        for foreign_key in ExternalIdentity.__table__.c.user_id.foreign_keys
    }

    assert user_id_foreign_keys == {
        "users.id",
    }