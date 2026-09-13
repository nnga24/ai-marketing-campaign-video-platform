from modules.creative_intelligence.models import CreativeVariant
from modules.content_production.models import (
    AssetRequirement,
    ProductionAsset,
    ProductionRun,
    Storyboard,
    StoryboardScene,
    VideoBrief,
)
from datetime import datetime

from modules.content_production.enums import ProductionRunStatus

class ContentProductionInvariantError(ValueError):
    pass

_ALLOWED_PRODUCTION_RUN_TRANSITIONS: dict[
    ProductionRunStatus,
    frozenset[ProductionRunStatus],
] = {
    ProductionRunStatus.PENDING: frozenset({
        ProductionRunStatus.RUNNING,
        ProductionRunStatus.CANCELLED,
    }),
    ProductionRunStatus.RUNNING: frozenset({
        ProductionRunStatus.SUCCEEDED,
        ProductionRunStatus.PARTIAL,
        ProductionRunStatus.FAILED,
        ProductionRunStatus.CANCELLED,
    }),
    ProductionRunStatus.SUCCEEDED: frozenset(),
    ProductionRunStatus.PARTIAL: frozenset(),
    ProductionRunStatus.FAILED: frozenset(),
    ProductionRunStatus.CANCELLED: frozenset(),
}


def ensure_production_run_transition_allowed(
    *,
    production_run: ProductionRun,
    target_status: ProductionRunStatus,
) -> None:
    current_status = production_run.status

    if target_status not in _ALLOWED_PRODUCTION_RUN_TRANSITIONS[current_status]:
        raise ContentProductionInvariantError(
            "ProductionRun transition "
            f"{current_status.value} -> {target_status.value} "
            "is not allowed."
        )


def transition_production_run(
    *,
    production_run: ProductionRun,
    target_status: ProductionRunStatus,
    transitioned_at: datetime,
) -> ProductionRun:
    ensure_production_run_transition_allowed(
        production_run=production_run,
        target_status=target_status,
    )

    if target_status is ProductionRunStatus.RUNNING:
        production_run.status = target_status
        production_run.started_at = transitioned_at
        return production_run

    if (
        production_run.started_at is not None
        and transitioned_at < production_run.started_at
    ):
        raise ContentProductionInvariantError(
            "ProductionRun finished_at cannot be earlier than started_at."
        )

    production_run.status = target_status
    production_run.finished_at = transitioned_at

    return production_run

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

def ensure_storyboard_parent_matches_video_brief(
    *,
    video_brief: VideoBrief,
    parent: Storyboard | None,
) -> None:
    if parent is not None and parent.video_brief_id != video_brief.id:
        raise ContentProductionInvariantError(
            "Storyboard parent must belong to the same VideoBrief."
        )


def build_storyboard_version(
    *,
    video_brief: VideoBrief,
    parent: Storyboard | None = None,
) -> Storyboard:
    ensure_storyboard_parent_matches_video_brief(
        video_brief=video_brief,
        parent=parent,
    )

    return Storyboard(
        video_brief_id=video_brief.id,
        parent_version_id=parent.id if parent is not None else None,
        version=parent.version + 1 if parent is not None else 1,
    )

def ensure_production_asset_matches_run_storyboard(
    *,
    production_run: ProductionRun,
    asset_requirement: AssetRequirement,
    storyboard_scene: StoryboardScene,
) -> None:
    if asset_requirement.storyboard_scene_id != storyboard_scene.id:
        raise ContentProductionInvariantError(
            "AssetRequirement must belong to the supplied StoryboardScene."
        )

    if production_run.storyboard_id != storyboard_scene.storyboard_id:
        raise ContentProductionInvariantError(
            "AssetRequirement must belong to the Storyboard "
            "executed by the ProductionRun."
        )


def build_production_asset(
    *,
    production_run: ProductionRun,
    asset_requirement: AssetRequirement,
    storyboard_scene: StoryboardScene,
    storage_uri: str,
    provider_key: str | None = None,
    provider_asset_id: str | None = None,
    mime_type: str | None = None,
) -> ProductionAsset:
    ensure_production_asset_matches_run_storyboard(
        production_run=production_run,
        asset_requirement=asset_requirement,
        storyboard_scene=storyboard_scene,
    )

    return ProductionAsset(
        production_run_id=production_run.id,
        asset_requirement_id=asset_requirement.id,
        asset_kind=asset_requirement.asset_kind,
        storage_uri=storage_uri,
        provider_key=provider_key,
        provider_asset_id=provider_asset_id,
        mime_type=mime_type,
    )