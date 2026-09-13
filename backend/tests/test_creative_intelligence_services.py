import uuid

import pytest

from modules.campaign_planning.models import ContentItem
from modules.creative_intelligence.models import (
    CreativeBrief,
    CreativeDecision,
    CreativeVariant,
)
from modules.creative_intelligence.services import (
    CreativeIntelligenceInvariantError,
    build_creative_brief_version,
    build_creative_variant_decision,
    ensure_creative_brief_parent_matches_content_item,
    ensure_creative_variant_decision_matches_brief,
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

def test_creative_variant_decision_invariant_accepts_same_brief():
    creative_brief_id = uuid.uuid4()

    variant = CreativeVariant(
        id=uuid.uuid4(),
        creative_brief_id=creative_brief_id,
        variant_key="A",
        hypothesis="Curiosity hook may improve retention.",
        source_type=SourceType.AI_SUGGESTED,
    )

    decision = CreativeDecision(
        id=uuid.uuid4(),
        creative_brief_id=creative_brief_id,
        decision_kind="HOOK_DIRECTION",
        statement="Open with a curiosity-driven hook.",
        source_type=SourceType.AI_SUGGESTED,
    )

    ensure_creative_variant_decision_matches_brief(
        creative_variant=variant,
        creative_decision=decision,
    )


def test_creative_variant_decision_invariant_rejects_cross_brief():
    variant = CreativeVariant(
        id=uuid.uuid4(),
        creative_brief_id=uuid.uuid4(),
        variant_key="A",
        hypothesis="Curiosity hook may improve retention.",
        source_type=SourceType.AI_SUGGESTED,
    )

    decision = CreativeDecision(
        id=uuid.uuid4(),
        creative_brief_id=uuid.uuid4(),
        decision_kind="HOOK_DIRECTION",
        statement="Open with a curiosity-driven hook.",
        source_type=SourceType.AI_SUGGESTED,
    )

    with pytest.raises(
        CreativeIntelligenceInvariantError,
        match="CreativeVariant and CreativeDecision must belong to the same CreativeBrief.",
    ):
        ensure_creative_variant_decision_matches_brief(
            creative_variant=variant,
            creative_decision=decision,
        )


def test_build_creative_variant_decision():
    creative_brief_id = uuid.uuid4()

    variant = CreativeVariant(
        id=uuid.uuid4(),
        creative_brief_id=creative_brief_id,
        variant_key="A",
        hypothesis="Curiosity hook may improve retention.",
        source_type=SourceType.AI_SUGGESTED,
    )

    decision = CreativeDecision(
        id=uuid.uuid4(),
        creative_brief_id=creative_brief_id,
        decision_kind="HOOK_DIRECTION",
        statement="Open with a curiosity-driven hook.",
        source_type=SourceType.AI_SUGGESTED,
    )

    link = build_creative_variant_decision(
        creative_variant=variant,
        creative_decision=decision,
    )

    assert link.creative_variant_id == variant.id
    assert link.creative_decision_id == decision.id


def test_build_creative_variant_decision_rejects_cross_brief():
    variant = CreativeVariant(
        id=uuid.uuid4(),
        creative_brief_id=uuid.uuid4(),
        variant_key="A",
        hypothesis="Curiosity hook may improve retention.",
        source_type=SourceType.AI_SUGGESTED,
    )

    decision = CreativeDecision(
        id=uuid.uuid4(),
        creative_brief_id=uuid.uuid4(),
        decision_kind="HOOK_DIRECTION",
        statement="Open with a curiosity-driven hook.",
        source_type=SourceType.AI_SUGGESTED,
    )

    with pytest.raises(CreativeIntelligenceInvariantError):
        build_creative_variant_decision(
            creative_variant=variant,
            creative_decision=decision,
        )