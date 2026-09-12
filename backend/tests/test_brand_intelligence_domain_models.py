from sqlalchemy import UniqueConstraint

from modules.brand_intelligence.enums import (
    FactVerificationStatus,
    ProductFactType,
)
from modules.brand_intelligence.models import (
    Brand,
    BrandProfile,
    Product,
    ProductClaim,
    ProductClaimEvidence,
    ProductFact,
    ProductTruth,
)
from modules.common.enums import EntityStatus


def test_fact_verification_status_values():
    assert [status.value for status in FactVerificationStatus] == [
        "CONFIRMED",
        "PROPOSED",
        "UNKNOWN",
    ]


def test_product_fact_type_values():
    assert [fact_type.value for fact_type in ProductFactType] == [
        "DESCRIPTION",
        "FEATURE",
        "INGREDIENT",
        "SPECIFICATION",
        "USAGE",
        "AVAILABILITY",
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


def test_brand_profile_table_contract():
    columns = BrandProfile.__table__.columns

    assert set(columns.keys()) == {
        "id",
        "brand_id",
        "parent_version_id",
        "overview",
        "created_at",
        "updated_at",
        "status",
        "source_type",
        "version",
        "schema_version",
        "is_outdated",
    }

    assert columns["brand_id"].nullable is False
    assert columns["parent_version_id"].nullable is True
    assert columns["overview"].nullable is True
    assert columns["source_type"].nullable is False

    brand_fk = next(iter(columns["brand_id"].foreign_keys))
    parent_fk = next(iter(columns["parent_version_id"].foreign_keys))

    assert brand_fk.target_fullname == "brands.id"
    assert brand_fk.ondelete == "CASCADE"

    assert parent_fk.target_fullname == "brand_profiles.id"
    assert parent_fk.ondelete == "SET NULL"


def test_brand_profile_version_is_unique_per_brand():
    unique_constraints = [
        constraint
        for constraint in BrandProfile.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    ]

    assert any(
        constraint.name == "uq_brand_profiles_brand_version"
        and [column.name for column in constraint.columns]
        == ["brand_id", "version"]
        for constraint in unique_constraints
    )


def test_brand_profile_version_metadata_defaults():
    columns = BrandProfile.__table__.columns

    assert columns["version"].default.arg == 1
    assert str(columns["version"].server_default.arg) == "1"

    assert columns["schema_version"].default.arg == 1
    assert str(columns["schema_version"].server_default.arg) == "1"

    assert columns["is_outdated"].default.arg is False
    assert str(columns["is_outdated"].server_default.arg) == "false"


def test_brand_profile_requires_explicit_provenance():
    source_type_column = BrandProfile.__table__.columns["source_type"]

    assert source_type_column.nullable is False
    assert source_type_column.default is None
    assert source_type_column.server_default is None


def test_product_table_contract():
    columns = Product.__table__.columns

    assert set(columns.keys()) == {
        "id",
        "brand_id",
        "name",
        "slug",
        "created_at",
        "updated_at",
        "status",
    }

    assert columns["id"].primary_key is True
    assert columns["brand_id"].nullable is False
    assert columns["name"].nullable is False
    assert columns["slug"].nullable is False

    brand_fk = next(iter(columns["brand_id"].foreign_keys))

    assert brand_fk.target_fullname == "brands.id"
    assert brand_fk.ondelete == "CASCADE"


def test_product_slug_is_unique_per_brand():
    unique_constraints = [
        constraint
        for constraint in Product.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    ]

    assert any(
        constraint.name == "uq_products_brand_slug"
        and [column.name for column in constraint.columns]
        == ["brand_id", "slug"]
        for constraint in unique_constraints
    )


def test_product_defaults_to_draft():
    status_column = Product.__table__.columns["status"]

    assert status_column.default.arg == EntityStatus.DRAFT
    assert str(status_column.server_default.arg) == "DRAFT"

def test_product_truth_table_contract():
    columns = ProductTruth.__table__.columns

    assert set(columns.keys()) == {
        "id",
        "product_id",
        "parent_version_id",
        "created_at",
        "updated_at",
        "status",
        "version",
        "schema_version",
        "is_outdated",
    }

    assert columns["product_id"].nullable is False
    assert columns["parent_version_id"].nullable is True

    product_fk = next(iter(columns["product_id"].foreign_keys))
    parent_fk = next(iter(columns["parent_version_id"].foreign_keys))

    assert product_fk.target_fullname == "products.id"
    assert product_fk.ondelete == "CASCADE"

    assert parent_fk.target_fullname == "product_truths.id"
    assert parent_fk.ondelete == "SET NULL"


def test_product_truth_version_is_unique_per_product():
    unique_constraints = [
        constraint
        for constraint in ProductTruth.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    ]

    assert any(
        constraint.name == "uq_product_truths_product_version"
        and [column.name for column in constraint.columns]
        == ["product_id", "version"]
        for constraint in unique_constraints
    )


def test_product_truth_metadata_defaults():
    columns = ProductTruth.__table__.columns

    assert columns["status"].default.arg == EntityStatus.DRAFT
    assert str(columns["status"].server_default.arg) == "DRAFT"

    assert columns["version"].default.arg == 1
    assert str(columns["version"].server_default.arg) == "1"

    assert columns["schema_version"].default.arg == 1
    assert str(columns["schema_version"].server_default.arg) == "1"

    assert columns["is_outdated"].default.arg is False
    assert str(columns["is_outdated"].server_default.arg) == "false"


def test_product_fact_table_contract():
    columns = ProductFact.__table__.columns

    assert set(columns.keys()) == {
        "id",
        "product_truth_id",
        "fact_type",
        "statement",
        "verification_status",
        "created_at",
        "updated_at",
        "source_type",
    }

    assert columns["product_truth_id"].nullable is False
    assert columns["fact_type"].nullable is False
    assert columns["statement"].nullable is False
    assert columns["verification_status"].nullable is False
    assert columns["source_type"].nullable is False

    product_truth_fk = next(
        iter(columns["product_truth_id"].foreign_keys)
    )

    assert product_truth_fk.target_fullname == "product_truths.id"
    assert product_truth_fk.ondelete == "CASCADE"


def test_product_fact_requires_explicit_source_and_verification():
    columns = ProductFact.__table__.columns

    source_type_column = columns["source_type"]
    verification_column = columns["verification_status"]

    assert source_type_column.default is None
    assert source_type_column.server_default is None

    assert verification_column.default is None
    assert verification_column.server_default is None

def test_product_claim_table_contract():
    columns = ProductClaim.__table__.columns

    assert set(columns.keys()) == {
        "id",
        "product_truth_id",
        "statement",
        "verification_status",
        "created_at",
        "updated_at",
        "source_type",
    }

    assert columns["product_truth_id"].nullable is False
    assert columns["statement"].nullable is False
    assert columns["verification_status"].nullable is False
    assert columns["source_type"].nullable is False

    product_truth_fk = next(
        iter(columns["product_truth_id"].foreign_keys)
    )

    assert product_truth_fk.target_fullname == "product_truths.id"
    assert product_truth_fk.ondelete == "CASCADE"


def test_product_claim_requires_explicit_source_and_verification():
    columns = ProductClaim.__table__.columns

    source_type_column = columns["source_type"]
    verification_column = columns["verification_status"]

    assert source_type_column.default is None
    assert source_type_column.server_default is None

    assert verification_column.default is None
    assert verification_column.server_default is None


def test_product_claim_evidence_table_contract():
    columns = ProductClaimEvidence.__table__.columns

    assert set(columns.keys()) == {
        "id",
        "product_claim_id",
        "description",
        "reference_uri",
        "verification_status",
        "created_at",
        "updated_at",
        "source_type",
    }

    assert columns["product_claim_id"].nullable is False
    assert columns["description"].nullable is False
    assert columns["reference_uri"].nullable is True
    assert columns["verification_status"].nullable is False
    assert columns["source_type"].nullable is False

    product_claim_fk = next(
        iter(columns["product_claim_id"].foreign_keys)
    )

    assert product_claim_fk.target_fullname == "product_claims.id"
    assert product_claim_fk.ondelete == "CASCADE"


def test_product_claim_evidence_requires_explicit_source_and_verification():
    columns = ProductClaimEvidence.__table__.columns

    source_type_column = columns["source_type"]
    verification_column = columns["verification_status"]

    assert source_type_column.default is None
    assert source_type_column.server_default is None

    assert verification_column.default is None
    assert verification_column.server_default is None