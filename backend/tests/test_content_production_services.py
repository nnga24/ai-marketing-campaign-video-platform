import uuid

import pytest

from modules.common.enums import SourceType
from modules.content_production.models import (
    AssetRequirement,
    FinalAsset,
    FinalAssetInput,
    ProductionAsset,
    ProductionRun,
    Storyboard,
    StoryboardScene,
    VideoBrief,
)
from modules.content_production.services import (
    ContentProductionInvariantError,
    build_storyboard_version,
    build_video_brief_version,
    ensure_storyboard_parent_matches_video_brief,
    ensure_video_brief_parent_matches_creative_variant,
    ensure_production_run_transition_allowed,
    transition_production_run,
    build_production_asset,
    ensure_production_asset_matches_run_storyboard,
    build_final_asset_input,
    ensure_final_asset_input_matches_production_run,
)
from modules.creative_intelligence.models import CreativeVariant
from datetime import datetime, timezone

from modules.content_production.enums import ProductionRunStatus

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

def test_storyboard_parent_invariant_accepts_same_video_brief():
    video_brief = VideoBrief(
        id=uuid.uuid4(),
        creative_variant_id=uuid.uuid4(),
        version=1,
    )

    parent = Storyboard(
        id=uuid.uuid4(),
        video_brief_id=video_brief.id,
        version=1,
    )

    ensure_storyboard_parent_matches_video_brief(
        video_brief=video_brief,
        parent=parent,
    )


def test_storyboard_parent_invariant_rejects_cross_video_brief():
    video_brief = VideoBrief(
        id=uuid.uuid4(),
        creative_variant_id=uuid.uuid4(),
        version=1,
    )

    parent = Storyboard(
        id=uuid.uuid4(),
        video_brief_id=uuid.uuid4(),
        version=1,
    )

    with pytest.raises(
        ContentProductionInvariantError,
        match="Storyboard parent must belong to the same VideoBrief.",
    ):
        ensure_storyboard_parent_matches_video_brief(
            video_brief=video_brief,
            parent=parent,
        )


def test_build_storyboard_first_version():
    video_brief = VideoBrief(
        id=uuid.uuid4(),
        creative_variant_id=uuid.uuid4(),
        version=1,
    )

    storyboard = build_storyboard_version(
        video_brief=video_brief,
    )

    assert storyboard.video_brief_id == video_brief.id
    assert storyboard.parent_version_id is None
    assert storyboard.version == 1


def test_build_storyboard_next_version():
    video_brief = VideoBrief(
        id=uuid.uuid4(),
        creative_variant_id=uuid.uuid4(),
        version=1,
    )

    parent = Storyboard(
        id=uuid.uuid4(),
        video_brief_id=video_brief.id,
        version=1,
    )

    storyboard = build_storyboard_version(
        video_brief=video_brief,
        parent=parent,
    )

    assert storyboard.video_brief_id == video_brief.id
    assert storyboard.parent_version_id == parent.id
    assert storyboard.version == 2


def test_build_storyboard_rejects_cross_video_brief_parent():
    video_brief = VideoBrief(
        id=uuid.uuid4(),
        creative_variant_id=uuid.uuid4(),
        version=1,
    )

    parent = Storyboard(
        id=uuid.uuid4(),
        video_brief_id=uuid.uuid4(),
        version=1,
    )

    with pytest.raises(ContentProductionInvariantError):
        build_storyboard_version(
            video_brief=video_brief,
            parent=parent,
        )

def test_production_run_transition_allows_pending_to_running():
    production_run = ProductionRun(
        id=uuid.uuid4(),
        storyboard_id=uuid.uuid4(),
        status=ProductionRunStatus.PENDING,
    )

    ensure_production_run_transition_allowed(
        production_run=production_run,
        target_status=ProductionRunStatus.RUNNING,
    )


def test_production_run_transition_allows_pending_to_cancelled():
    production_run = ProductionRun(
        id=uuid.uuid4(),
        storyboard_id=uuid.uuid4(),
        status=ProductionRunStatus.PENDING,
    )

    ensure_production_run_transition_allowed(
        production_run=production_run,
        target_status=ProductionRunStatus.CANCELLED,
    )


def test_production_run_transition_allows_running_to_terminal_statuses():
    production_run = ProductionRun(
        id=uuid.uuid4(),
        storyboard_id=uuid.uuid4(),
        status=ProductionRunStatus.RUNNING,
    )

    for target_status in (
        ProductionRunStatus.SUCCEEDED,
        ProductionRunStatus.PARTIAL,
        ProductionRunStatus.FAILED,
        ProductionRunStatus.CANCELLED,
    ):
        ensure_production_run_transition_allowed(
            production_run=production_run,
            target_status=target_status,
        )


def test_production_run_transition_rejects_invalid_transition():
    production_run = ProductionRun(
        id=uuid.uuid4(),
        storyboard_id=uuid.uuid4(),
        status=ProductionRunStatus.PENDING,
    )

    with pytest.raises(
        ContentProductionInvariantError,
        match="ProductionRun transition PENDING -> SUCCEEDED is not allowed.",
    ):
        ensure_production_run_transition_allowed(
            production_run=production_run,
            target_status=ProductionRunStatus.SUCCEEDED,
        )


def test_transition_production_run_to_running_sets_started_at():
    transitioned_at = datetime(
        2026,
        9,
        13,
        10,
        0,
        tzinfo=timezone.utc,
    )

    production_run = ProductionRun(
        id=uuid.uuid4(),
        storyboard_id=uuid.uuid4(),
        status=ProductionRunStatus.PENDING,
    )

    result = transition_production_run(
        production_run=production_run,
        target_status=ProductionRunStatus.RUNNING,
        transitioned_at=transitioned_at,
    )

    assert result is production_run
    assert production_run.status is ProductionRunStatus.RUNNING
    assert production_run.started_at == transitioned_at
    assert production_run.finished_at is None


def test_transition_production_run_to_terminal_sets_finished_at():
    started_at = datetime(
        2026,
        9,
        13,
        10,
        0,
        tzinfo=timezone.utc,
    )
    finished_at = datetime(
        2026,
        9,
        13,
        10,
        5,
        tzinfo=timezone.utc,
    )

    production_run = ProductionRun(
        id=uuid.uuid4(),
        storyboard_id=uuid.uuid4(),
        status=ProductionRunStatus.RUNNING,
        started_at=started_at,
    )

    transition_production_run(
        production_run=production_run,
        target_status=ProductionRunStatus.SUCCEEDED,
        transitioned_at=finished_at,
    )

    assert production_run.status is ProductionRunStatus.SUCCEEDED
    assert production_run.started_at == started_at
    assert production_run.finished_at == finished_at


def test_transition_production_run_pending_to_cancelled_sets_finished_at():
    cancelled_at = datetime(
        2026,
        9,
        13,
        10,
        0,
        tzinfo=timezone.utc,
    )

    production_run = ProductionRun(
        id=uuid.uuid4(),
        storyboard_id=uuid.uuid4(),
        status=ProductionRunStatus.PENDING,
    )

    transition_production_run(
        production_run=production_run,
        target_status=ProductionRunStatus.CANCELLED,
        transitioned_at=cancelled_at,
    )

    assert production_run.status is ProductionRunStatus.CANCELLED
    assert production_run.started_at is None
    assert production_run.finished_at == cancelled_at


def test_transition_production_run_rejects_finish_before_start():
    started_at = datetime(
        2026,
        9,
        13,
        10,
        5,
        tzinfo=timezone.utc,
    )
    invalid_finished_at = datetime(
        2026,
        9,
        13,
        10,
        0,
        tzinfo=timezone.utc,
    )

    production_run = ProductionRun(
        id=uuid.uuid4(),
        storyboard_id=uuid.uuid4(),
        status=ProductionRunStatus.RUNNING,
        started_at=started_at,
    )

    with pytest.raises(
        ContentProductionInvariantError,
        match="ProductionRun finished_at cannot be earlier than started_at.",
    ):
        transition_production_run(
            production_run=production_run,
            target_status=ProductionRunStatus.FAILED,
            transitioned_at=invalid_finished_at,
        )

    assert production_run.status is ProductionRunStatus.RUNNING
    assert production_run.finished_at is None

def test_production_asset_invariant_accepts_matching_storyboard():
    storyboard_id = uuid.uuid4()

    scene = StoryboardScene(
        id=uuid.uuid4(),
        storyboard_id=storyboard_id,
        scene_key="scene-1",
        sequence_index=1,
        purpose="HOOK",
        source_type=SourceType.AI_SUGGESTED,
    )

    requirement = AssetRequirement(
        id=uuid.uuid4(),
        storyboard_scene_id=scene.id,
        requirement_key="hero-visual",
        asset_kind="IMAGE",
        description="Product hero visual.",
        source_type=SourceType.AI_SUGGESTED,
    )

    production_run = ProductionRun(
        id=uuid.uuid4(),
        storyboard_id=storyboard_id,
        status=ProductionRunStatus.PENDING,
    )

    ensure_production_asset_matches_run_storyboard(
        production_run=production_run,
        asset_requirement=requirement,
        storyboard_scene=scene,
    )


def test_production_asset_invariant_rejects_requirement_from_other_scene():
    storyboard_id = uuid.uuid4()

    scene = StoryboardScene(
        id=uuid.uuid4(),
        storyboard_id=storyboard_id,
        scene_key="scene-1",
        sequence_index=1,
        purpose="HOOK",
        source_type=SourceType.AI_SUGGESTED,
    )

    requirement = AssetRequirement(
        id=uuid.uuid4(),
        storyboard_scene_id=uuid.uuid4(),
        requirement_key="hero-visual",
        asset_kind="IMAGE",
        description="Product hero visual.",
        source_type=SourceType.AI_SUGGESTED,
    )

    production_run = ProductionRun(
        id=uuid.uuid4(),
        storyboard_id=storyboard_id,
        status=ProductionRunStatus.PENDING,
    )

    with pytest.raises(
        ContentProductionInvariantError,
        match="AssetRequirement must belong to the supplied StoryboardScene.",
    ):
        ensure_production_asset_matches_run_storyboard(
            production_run=production_run,
            asset_requirement=requirement,
            storyboard_scene=scene,
        )


def test_production_asset_invariant_rejects_cross_storyboard_requirement():
    scene = StoryboardScene(
        id=uuid.uuid4(),
        storyboard_id=uuid.uuid4(),
        scene_key="scene-1",
        sequence_index=1,
        purpose="HOOK",
        source_type=SourceType.AI_SUGGESTED,
    )

    requirement = AssetRequirement(
        id=uuid.uuid4(),
        storyboard_scene_id=scene.id,
        requirement_key="hero-visual",
        asset_kind="IMAGE",
        description="Product hero visual.",
        source_type=SourceType.AI_SUGGESTED,
    )

    production_run = ProductionRun(
        id=uuid.uuid4(),
        storyboard_id=uuid.uuid4(),
        status=ProductionRunStatus.PENDING,
    )

    with pytest.raises(
        ContentProductionInvariantError,
        match=(
            "AssetRequirement must belong to the Storyboard "
            "executed by the ProductionRun."
        ),
    ):
        ensure_production_asset_matches_run_storyboard(
            production_run=production_run,
            asset_requirement=requirement,
            storyboard_scene=scene,
        )


def test_build_production_asset_uses_requirement_asset_kind():
    storyboard_id = uuid.uuid4()

    scene = StoryboardScene(
        id=uuid.uuid4(),
        storyboard_id=storyboard_id,
        scene_key="scene-1",
        sequence_index=1,
        purpose="HOOK",
        source_type=SourceType.AI_SUGGESTED,
    )

    requirement = AssetRequirement(
        id=uuid.uuid4(),
        storyboard_scene_id=scene.id,
        requirement_key="hero-visual",
        asset_kind="IMAGE",
        description="Product hero visual.",
        source_type=SourceType.AI_SUGGESTED,
    )

    production_run = ProductionRun(
        id=uuid.uuid4(),
        storyboard_id=storyboard_id,
        status=ProductionRunStatus.RUNNING,
    )

    asset = build_production_asset(
        production_run=production_run,
        asset_requirement=requirement,
        storyboard_scene=scene,
        storage_uri="storage://production/image-001.webp",
        provider_key="example-provider",
        provider_asset_id="asset-001",
        mime_type="image/webp",
    )

    assert asset.production_run_id == production_run.id
    assert asset.asset_requirement_id == requirement.id
    assert asset.asset_kind == requirement.asset_kind
    assert asset.storage_uri == "storage://production/image-001.webp"
    assert asset.provider_key == "example-provider"
    assert asset.provider_asset_id == "asset-001"
    assert asset.mime_type == "image/webp"


def test_final_asset_input_invariant_accepts_same_production_run():
    production_run_id = uuid.uuid4()

    final_asset = FinalAsset(
        id=uuid.uuid4(),
        production_run_id=production_run_id,
        output_key="master",
        asset_kind="VIDEO",
        storage_uri="storage://final/master.mp4",
    )

    production_asset = ProductionAsset(
        id=uuid.uuid4(),
        production_run_id=production_run_id,
        asset_requirement_id=uuid.uuid4(),
        asset_kind="IMAGE",
        storage_uri="storage://production/image.webp",
    )

    ensure_final_asset_input_matches_production_run(
        final_asset=final_asset,
        production_asset=production_asset,
    )


def test_final_asset_input_invariant_rejects_cross_run_asset():
    final_asset = FinalAsset(
        id=uuid.uuid4(),
        production_run_id=uuid.uuid4(),
        output_key="master",
        asset_kind="VIDEO",
        storage_uri="storage://final/master.mp4",
    )

    production_asset = ProductionAsset(
        id=uuid.uuid4(),
        production_run_id=uuid.uuid4(),
        asset_requirement_id=uuid.uuid4(),
        asset_kind="IMAGE",
        storage_uri="storage://production/image.webp",
    )

    with pytest.raises(
        ContentProductionInvariantError,
        match=(
            "ProductionAsset must belong to the same ProductionRun "
            "as the FinalAsset."
        ),
    ):
        ensure_final_asset_input_matches_production_run(
            final_asset=final_asset,
            production_asset=production_asset,
        )


def test_build_final_asset_input():
    production_run_id = uuid.uuid4()

    final_asset = FinalAsset(
        id=uuid.uuid4(),
        production_run_id=production_run_id,
        output_key="master",
        asset_kind="VIDEO",
        storage_uri="storage://final/master.mp4",
    )

    production_asset = ProductionAsset(
        id=uuid.uuid4(),
        production_run_id=production_run_id,
        asset_requirement_id=uuid.uuid4(),
        asset_kind="IMAGE",
        storage_uri="storage://production/image.webp",
    )

    link = build_final_asset_input(
        final_asset=final_asset,
        production_asset=production_asset,
    )

    assert link.final_asset_id == final_asset.id
    assert link.production_asset_id == production_asset.id