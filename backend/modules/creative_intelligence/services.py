from modules.campaign_planning.models import ContentItem
from modules.creative_intelligence.models import (
    CreativeBrief,
    CreativeDecision,
    CreativeVariant,
    CreativeVariantDecision,
)


class CreativeIntelligenceInvariantError(ValueError):
    pass


def ensure_creative_brief_parent_matches_content_item(
    *,
    content_item: ContentItem,
    parent: CreativeBrief | None,
) -> None:
    if parent is not None and parent.content_item_id != content_item.id:
        raise CreativeIntelligenceInvariantError(
            "CreativeBrief parent must belong to the same ContentItem."
        )

def build_creative_brief_version(
    *,
    content_item: ContentItem,
    parent: CreativeBrief | None = None,
) -> CreativeBrief:
    ensure_creative_brief_parent_matches_content_item(
        content_item=content_item,
        parent=parent,
    )

    return CreativeBrief(
        content_item_id=content_item.id,
        parent_version_id=parent.id if parent is not None else None,
        version=parent.version + 1 if parent is not None else 1,
    )

def ensure_creative_variant_decision_matches_brief(
    *,
    creative_variant: CreativeVariant,
    creative_decision: CreativeDecision,
) -> None:
    if creative_variant.creative_brief_id != creative_decision.creative_brief_id:
        raise CreativeIntelligenceInvariantError(
            "CreativeVariant and CreativeDecision must belong to the same CreativeBrief."
        )


def build_creative_variant_decision(
    *,
    creative_variant: CreativeVariant,
    creative_decision: CreativeDecision,
) -> CreativeVariantDecision:
    ensure_creative_variant_decision_matches_brief(
        creative_variant=creative_variant,
        creative_decision=creative_decision,
    )

    return CreativeVariantDecision(
        creative_variant_id=creative_variant.id,
        creative_decision_id=creative_decision.id,
    )