from sqlalchemy import UniqueConstraint

from modules.content_production.models import (
    Storyboard,
    StoryboardScene,
    VideoBrief,
    VideoBriefInstruction,
)


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

def test_video_brief_instruction_table_contract():
    columns = VideoBriefInstruction.__table__.columns

    assert set(columns.keys()) == {
        "id",
        "video_brief_id",
        "instruction_kind",
        "statement",
        "rationale",
        "created_at",
        "updated_at",
        "source_type",
    }

    assert columns["video_brief_id"].nullable is False
    assert columns["instruction_kind"].nullable is False
    assert columns["statement"].nullable is False
    assert columns["rationale"].nullable is True
    assert columns["source_type"].nullable is False

    video_brief_fk = next(
        iter(columns["video_brief_id"].foreign_keys)
    )

    assert video_brief_fk.target_fullname == "video_briefs.id"
    assert video_brief_fk.ondelete == "CASCADE"

    assert "status" not in columns
    assert "version" not in columns
    assert "schema_version" not in columns
    assert "is_outdated" not in columns


def test_video_brief_instruction_kind_is_not_unique():
    assert VideoBriefInstruction.__table__.columns["instruction_kind"].unique is not True

def test_storyboard_table_contract():
    columns = Storyboard.__table__.columns

    assert set(columns.keys()) == {
        "id",
        "video_brief_id",
        "parent_version_id",
        "created_at",
        "updated_at",
        "status",
        "version",
        "schema_version",
        "is_outdated",
    }

    assert columns["video_brief_id"].nullable is False
    assert columns["parent_version_id"].nullable is True

    video_brief_fk = next(
        iter(columns["video_brief_id"].foreign_keys)
    )
    parent_version_fk = next(
        iter(columns["parent_version_id"].foreign_keys)
    )

    assert video_brief_fk.target_fullname == "video_briefs.id"
    assert video_brief_fk.ondelete == "CASCADE"

    assert parent_version_fk.target_fullname == "storyboards.id"
    assert parent_version_fk.ondelete == "SET NULL"

    assert "source_type" not in columns


def test_storyboard_video_brief_version_unique_constraint():
    unique_constraints = [
        constraint
        for constraint in Storyboard.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    ]

    matching_constraint = next(
        constraint
        for constraint in unique_constraints
        if constraint.name == "uq_storyboards_video_brief_version"
    )

    assert [column.name for column in matching_constraint.columns] == [
        "video_brief_id",
        "version",
    ]

def test_storyboard_scene_table_contract():
    columns = StoryboardScene.__table__.columns

    assert set(columns.keys()) == {
        "id",
        "storyboard_id",
        "scene_key",
        "sequence_index",
        "purpose",
        "voiceover_text",
        "visual_direction",
        "on_screen_text",
        "created_at",
        "updated_at",
        "source_type",
    }

    assert columns["storyboard_id"].nullable is False
    assert columns["scene_key"].nullable is False
    assert columns["sequence_index"].nullable is False
    assert columns["purpose"].nullable is False
    assert columns["voiceover_text"].nullable is True
    assert columns["visual_direction"].nullable is True
    assert columns["on_screen_text"].nullable is True
    assert columns["source_type"].nullable is False

    storyboard_fk = next(
        iter(columns["storyboard_id"].foreign_keys)
    )

    assert storyboard_fk.target_fullname == "storyboards.id"
    assert storyboard_fk.ondelete == "CASCADE"

    assert "status" not in columns
    assert "version" not in columns
    assert "schema_version" not in columns
    assert "is_outdated" not in columns


def test_storyboard_scene_unique_constraints():
    unique_constraints = {
        constraint.name: [column.name for column in constraint.columns]
        for constraint in StoryboardScene.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    }

    assert unique_constraints["uq_storyboard_scenes_storyboard_key"] == [
        "storyboard_id",
        "scene_key",
    ]

    assert unique_constraints["uq_storyboard_scenes_storyboard_sequence"] == [
        "storyboard_id",
        "sequence_index",
    ]