import uuid

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint, Uuid
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