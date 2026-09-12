from sqlalchemy import UniqueConstraint

from modules.brand_intelligence.enums import FactVerificationStatus
from modules.brand_intelligence.models import Brand
from modules.common.enums import EntityStatus


def test_fact_verification_status_values():
    assert [status.value for status in FactVerificationStatus] == [
        "CONFIRMED",
        "PROPOSED",
        "UNKNOWN",
    ]


def test_brand_table_contract():
    columns = Brand.__table__.columns

    assert set(columns.keys()) == {
        "id",
        "workspace_id",
        "name",
        "slug",
        "created_at",
        "updated_at",
        "status",
    }

    assert columns["id"].primary_key is True
    assert columns["workspace_id"].nullable is False
    assert columns["name"].nullable is False
    assert columns["slug"].nullable is False

    workspace_fk = next(iter(columns["workspace_id"].foreign_keys))

    assert workspace_fk.target_fullname == "workspaces.id"
    assert workspace_fk.ondelete == "CASCADE"


def test_brand_slug_is_unique_per_workspace():
    unique_constraints = [
        constraint
        for constraint in Brand.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    ]

    assert any(
        constraint.name == "uq_brands_workspace_slug"
        and [column.name for column in constraint.columns]
        == ["workspace_id", "slug"]
        for constraint in unique_constraints
    )


def test_brand_defaults_to_draft():
    status_column = Brand.__table__.columns["status"]

    assert status_column.default.arg == EntityStatus.DRAFT
    assert str(status_column.server_default.arg) == "DRAFT"