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


class CreativeBrief(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    LifecycleMixin,
    VersionMetadataMixin,
    Base,
):
    __tablename__ = "creative_briefs"

    __table_args__ = (
        UniqueConstraint(
            "content_item_id",
            "version",
            name="uq_creative_briefs_content_item_version",
        ),
    )

    content_item_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("content_items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    parent_version_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("creative_briefs.id", ondelete="SET NULL"),
        nullable=True,
    )

class CreativeDecision(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    ProvenanceMixin,
    Base,
):
    __tablename__ = "creative_decisions"

    creative_brief_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("creative_briefs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    decision_kind: Mapped[str] = mapped_column(
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

class CreativeVariant(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    ProvenanceMixin,
    Base,
):
    __tablename__ = "creative_variants"

    __table_args__ = (
        UniqueConstraint(
            "creative_brief_id",
            "variant_key",
            name="uq_creative_variants_brief_key",
        ),
    )

    creative_brief_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("creative_briefs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    variant_key: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    hypothesis: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )