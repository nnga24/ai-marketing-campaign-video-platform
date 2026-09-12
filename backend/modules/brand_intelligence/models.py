import uuid

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database.base import Base
from modules.common.mixins import (
    LifecycleMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
    VersionedArtifactMixin,
)


class Brand(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    LifecycleMixin,
    Base,
):
    __tablename__ = "brands"

    __table_args__ = (
        UniqueConstraint(
            "workspace_id",
            "slug",
            name="uq_brands_workspace_slug",
        ),
    )

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    slug: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

class BrandProfile(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    VersionedArtifactMixin,
    Base,
):
    __tablename__ = "brand_profiles"

    __table_args__ = (
        UniqueConstraint(
            "brand_id",
            "version",
            name="uq_brand_profiles_brand_version",
        ),
    )

    brand_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("brands.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    parent_version_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("brand_profiles.id", ondelete="SET NULL"),
        nullable=True,
    )

    overview: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )