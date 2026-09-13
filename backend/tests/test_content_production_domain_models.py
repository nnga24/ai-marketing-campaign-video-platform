from sqlalchemy import UniqueConstraint

from modules.content_production.models import VideoBrief


def test_video_brief_table_contract():
    columns = VideoBrief.__table__.columns

    assert set(columns.keys()) == {
        "id",
        "creative_variant_id",
        "parent_version_id",
        "created_at",
        "updated_at",
        "status",
        "version",
        "schema_version",
        "is_outdated",
    }

    assert columns["creative_variant_id"].nullable is False
    assert columns["parent_version_id"].nullable is True

    creative_variant_fk = next(
        iter(columns["creative_variant_id"].foreign_keys)
    )
    parent_version_fk = next(
        iter(columns["parent_version_id"].foreign_keys)
    )

    assert creative_variant_fk.target_fullname == "creative_variants.id"
    assert creative_variant_fk.ondelete == "CASCADE"

    assert parent_version_fk.target_fullname == "video_briefs.id"
    assert parent_version_fk.ondelete == "SET NULL"

    assert "source_type" not in columns


def test_video_brief_variant_version_unique_constraint():
    unique_constraints = [
        constraint
        for constraint in VideoBrief.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    ]

    matching_constraint = next(
        constraint
        for constraint in unique_constraints
        if constraint.name == "uq_video_briefs_creative_variant_version"
    )

    assert [column.name for column in matching_constraint.columns] == [
        "creative_variant_id",
        "version",
    ]