import uuid

from sqlalchemy import ForeignKey, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database.base import Base
from modules.common.mixins import (
    LifecycleMixin,
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