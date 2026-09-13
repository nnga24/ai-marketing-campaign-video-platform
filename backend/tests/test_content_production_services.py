import uuid

import pytest

from modules.common.enums import SourceType
from modules.content_production.models import VideoBrief
from modules.content_production.services import (
    ContentProductionInvariantError,
    build_video_brief_version,
    ensure_video_brief_parent_matches_creative_variant,
)
from modules.creative_intelligence.models import CreativeVariant


def build_creative_variant() -> CreativeVariant:
    return CreativeVariant(
        id=uuid.uuid4(),
        creative_brief_id=uuid.uuid4(),
        variant_key="A",
        hypothesis="Curiosity hook may improve retention.",
        source_type=SourceType.AI_SUGGESTED,
    )


def test_video_brief_parent_invariant_accepts_same_creative_variant():
    creative_variant = build_creative_variant()

    parent = VideoBrief(
        id=uuid.uuid4(),
        creative_variant_id=creative_variant.id,
        version=1,
    )

    ensure_video_brief_parent_matches_creative_variant(
        creative_variant=creative_variant,
        parent=parent,
    )


def test_video_brief_parent_invariant_rejects_cross_creative_variant():
    creative_variant = build_creative_variant()

    parent = VideoBrief(
        id=uuid.uuid4(),
        creative_variant_id=uuid.uuid4(),
        version=1,
    )

    with pytest.raises(
        ContentProductionInvariantError,
        match="VideoBrief parent must belong to the same CreativeVariant.",
    ):
        ensure_video_brief_parent_matches_creative_variant(
            creative_variant=creative_variant,
            parent=parent,
        )


def test_build_video_brief_first_version():
    creative_variant = build_creative_variant()

    video_brief = build_video_brief_version(
        creative_variant=creative_variant,
    )

    assert video_brief.creative_variant_id == creative_variant.id
    assert video_brief.parent_version_id is None
    assert video_brief.version == 1


def test_build_video_brief_next_version():
    creative_variant = build_creative_variant()

    parent = VideoBrief(
        id=uuid.uuid4(),
        creative_variant_id=creative_variant.id,
        version=1,
    )

    video_brief = build_video_brief_version(
        creative_variant=creative_variant,
        parent=parent,
    )

    assert video_brief.creative_variant_id == creative_variant.id
    assert video_brief.parent_version_id == parent.id
    assert video_brief.version == 2


def test_build_video_brief_rejects_cross_creative_variant_parent():
    creative_variant = build_creative_variant()

    parent = VideoBrief(
        id=uuid.uuid4(),
        creative_variant_id=uuid.uuid4(),
        version=1,
    )

    with pytest.raises(ContentProductionInvariantError):
        build_video_brief_version(
            creative_variant=creative_variant,
            parent=parent,
        )