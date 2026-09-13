from modules.creative_intelligence.models import CreativeVariant
from modules.content_production.models import VideoBrief


class ContentProductionInvariantError(ValueError):
    pass


def ensure_video_brief_parent_matches_creative_variant(
    *,
    creative_variant: CreativeVariant,
    parent: VideoBrief | None,
) -> None:
    if parent is not None and parent.creative_variant_id != creative_variant.id:
        raise ContentProductionInvariantError(
            "VideoBrief parent must belong to the same CreativeVariant."
        )


def build_video_brief_version(
    *,
    creative_variant: CreativeVariant,
    parent: VideoBrief | None = None,
) -> VideoBrief:
    ensure_video_brief_parent_matches_creative_variant(
        creative_variant=creative_variant,
        parent=parent,
    )

    return VideoBrief(
        creative_variant_id=creative_variant.id,
        parent_version_id=parent.id if parent is not None else None,
        version=parent.version + 1 if parent is not None else 1,
    )