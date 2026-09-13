from sqlalchemy import UniqueConstraint

from modules.creative_intelligence.models import (
    CreativeBrief,
    CreativeDecision,
    CreativeVariant,
)


def test_creative_brief_table_contract():
    columns = CreativeBrief.__table__.columns

    assert set(columns.keys()) == {
        "id",
        "content_item_id",
        "parent_version_id",
        "created_at",
        "updated_at",
        "status",
        "version",
        "schema_version",
        "is_outdated",
    }

    assert columns["content_item_id"].nullable is False
    assert columns["parent_version_id"].nullable is True
    assert columns["status"].nullable is False
    assert columns["version"].nullable is False
    assert columns["schema_version"].nullable is False
    assert columns["is_outdated"].nullable is False

    content_item_fk = next(
        iter(columns["content_item_id"].foreign_keys)
    )
    parent_fk = next(
        iter(columns["parent_version_id"].foreign_keys)
    )

    assert content_item_fk.target_fullname == "content_items.id"
    assert content_item_fk.ondelete == "CASCADE"

    assert parent_fk.target_fullname == "creative_briefs.id"
    assert parent_fk.ondelete == "SET NULL"

    assert "source_type" not in columns


def test_creative_brief_content_item_version_unique_constraint():
    unique_constraints = [
        constraint
        for constraint in CreativeBrief.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    ]

    matching_constraint = next(
        constraint
        for constraint in unique_constraints
        if constraint.name == "uq_creative_briefs_content_item_version"
    )

    assert [column.name for column in matching_constraint.columns] == [
        "content_item_id",
        "version",
    ]

def test_creative_decision_table_contract():
    columns = CreativeDecision.__table__.columns

    assert set(columns.keys()) == {
        "id",
        "creative_brief_id",
        "decision_kind",
        "statement",
        "rationale",
        "created_at",
        "updated_at",
        "source_type",
    }

    assert columns["creative_brief_id"].nullable is False
    assert columns["decision_kind"].nullable is False
    assert columns["statement"].nullable is False
    assert columns["rationale"].nullable is True
    assert columns["source_type"].nullable is False

    creative_brief_fk = next(
        iter(columns["creative_brief_id"].foreign_keys)
    )

    assert creative_brief_fk.target_fullname == "creative_briefs.id"
    assert creative_brief_fk.ondelete == "CASCADE"

    assert "status" not in columns
    assert "version" not in columns
    assert "schema_version" not in columns
    assert "is_outdated" not in columns


def test_creative_decision_kind_is_not_unique():
    unique_constraints = [
        constraint
        for constraint in CreativeDecision.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    ]

    assert all(
        [column.name for column in constraint.columns] != ["decision_kind"]
        for constraint in unique_constraints
    )

def test_creative_variant_table_contract():
    columns = CreativeVariant.__table__.columns

    assert set(columns.keys()) == {
        "id",
        "creative_brief_id",
        "variant_key",
        "hypothesis",
        "created_at",
        "updated_at",
        "source_type",
    }

    assert columns["creative_brief_id"].nullable is False
    assert columns["variant_key"].nullable is False
    assert columns["hypothesis"].nullable is False
    assert columns["source_type"].nullable is False

    creative_brief_fk = next(
        iter(columns["creative_brief_id"].foreign_keys)
    )

    assert creative_brief_fk.target_fullname == "creative_briefs.id"
    assert creative_brief_fk.ondelete == "CASCADE"

    assert "status" not in columns
    assert "version" not in columns
    assert "schema_version" not in columns
    assert "is_outdated" not in columns


def test_creative_variant_brief_key_unique_constraint():
    unique_constraints = [
        constraint
        for constraint in CreativeVariant.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    ]

    matching_constraint = next(
        constraint
        for constraint in unique_constraints
        if constraint.name == "uq_creative_variants_brief_key"
    )

    assert [column.name for column in matching_constraint.columns] == [
        "creative_brief_id",
        "variant_key",
    ]