import uuid
from datetime import datetime
from sqlalchemy import (
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from modules.content_production.enums import ProductionRunStatus
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database.base import Base
from modules.common.mixins import (
    LifecycleMixin,
    ProvenanceMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
    VersionMetadataMixin,
)


class VideoBrief(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    LifecycleMixin,
    VersionMetadataMixin,
    Base,
):
    __tablename__ = "video_briefs"

    __table_args__ = (
        UniqueConstraint(
            "creative_variant_id",
            "version",
            name="uq_video_briefs_creative_variant_version",
        ),
    )

    creative_variant_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("creative_variants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    parent_version_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("video_briefs.id", ondelete="SET NULL"),
        nullable=True,
    )

class VideoBriefInstruction(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    ProvenanceMixin,
    Base,
):
    __tablename__ = "video_brief_instructions"

    video_brief_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("video_briefs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    instruction_kind: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    statement: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    rationale: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

class Storyboard(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    LifecycleMixin,
    VersionMetadataMixin,
    Base,
):
    __tablename__ = "storyboards"

    __table_args__ = (
        UniqueConstraint(
            "video_brief_id",
            "version",
            name="uq_storyboards_video_brief_version",
        ),
    )

    video_brief_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("video_briefs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    parent_version_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("storyboards.id", ondelete="SET NULL"),
        nullable=True,
    )

class StoryboardScene(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    ProvenanceMixin,
    Base,
):
    __tablename__ = "storyboard_scenes"

    __table_args__ = (
        UniqueConstraint(
            "storyboard_id",
            "scene_key",
            name="uq_storyboard_scenes_storyboard_key",
        ),
        UniqueConstraint(
            "storyboard_id",
            "sequence_index",
            name="uq_storyboard_scenes_storyboard_sequence",
        ),
    )

    storyboard_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("storyboards.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    scene_key: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    sequence_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    purpose: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    voiceover_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    visual_direction: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    on_screen_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

class AssetRequirement(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    ProvenanceMixin,
    Base,
):
    __tablename__ = "asset_requirements"

    __table_args__ = (
        UniqueConstraint(
            "storyboard_scene_id",
            "requirement_key",
            name="uq_asset_requirements_scene_key",
        ),
    )

    storyboard_scene_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("storyboard_scenes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    requirement_key: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    asset_kind: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    rationale: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

class ProductionRun(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "production_runs"

    storyboard_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("storyboards.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    status: Mapped[ProductionRunStatus] = mapped_column(
        SAEnum(
            ProductionRunStatus,
            native_enum=False,
            length=32,
        ),
        nullable=False,
        default=ProductionRunStatus.PENDING,
        server_default=ProductionRunStatus.PENDING.value,
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

class ProductionAsset(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "production_assets"

    production_run_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("production_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    asset_requirement_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("asset_requirements.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    asset_kind: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    storage_uri: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    provider_key: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
    )

    provider_asset_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    mime_type: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
    )