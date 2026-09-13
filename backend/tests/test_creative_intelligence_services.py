import uuid

import pytest

from modules.campaign_planning.models import ContentItem
from modules.creative_intelligence.models import CreativeBrief
from modules.creative_intelligence.services import (
    CreativeIntelligenceInvariantError,
    build_creative_brief_version,
    ensure_creative_brief_parent_matches_content_item,
)
from modules.common.enums import SourceType


def build_content_item() -> ContentItem:
    return ContentItem(
        id=uuid.uuid4(),
        channel_plan_id=uuid.uuid4(),
        content_kind="short_video",
        source_type=SourceType.AI_SUGGESTED,
    )


def test_creative_brief_parent_invariant_accepts_same_content_item():
    content_item = build_content_item()

    parent = CreativeBrief(
        id=uuid.uuid4(),
        content_item_id=content_item.id,
        version=1,
    )

    ensure_creative_brief_parent_matches_content_item(
        content_item=content_item,
        parent=parent,
    )


def test_creative_brief_parent_invariant_rejects_cross_content_item():
    content_item = build_content_item()

    parent = CreativeBrief(
        id=uuid.uuid4(),
        content_item_id=uuid.uuid4(),
        version=1,
    )

    with pytest.raises(
        CreativeIntelligenceInvariantError,
        match="CreativeBrief parent must belong to the same ContentItem.",
    ):
        ensure_creative_brief_parent_matches_content_item(
            content_item=content_item,
            parent=parent,
        )


def test_build_creative_brief_first_version():
    content_item = build_content_item()

    brief = build_creative_brief_version(
        content_item=content_item,
    )

    assert brief.content_item_id == content_item.id
    assert brief.parent_version_id is None
    assert brief.version == 1


def test_build_creative_brief_next_version():
    content_item = build_content_item()

    parent = CreativeBrief(
        id=uuid.uuid4(),
        content_item_id=content_item.id,
        version=1,
    )

    brief = build_creative_brief_version(
        content_item=content_item,
        parent=parent,
    )

    assert brief.content_item_id == content_item.id
    assert brief.parent_version_id == parent.id
    assert brief.version == 2


def test_build_creative_brief_rejects_cross_content_item_parent():
    content_item = build_content_item()

    parent = CreativeBrief(
        id=uuid.uuid4(),
        content_item_id=uuid.uuid4(),
        version=1,
    )

    with pytest.raises(CreativeIntelligenceInvariantError):
        build_creative_brief_version(
            content_item=content_item,
            parent=parent,
        )