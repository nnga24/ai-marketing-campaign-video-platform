import uuid

from sqlalchemy import ForeignKey, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database.base import Base
from modules.common.mixins import (
    LifecycleMixin,
    ProvenanceMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
    VersionMetadataMixin,
)


class Campaign(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    LifecycleMixin,
    Base,
):
    __tablename__ = "campaigns"

    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "slug",
            name="uq_campaigns_project_slug",
        ),
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
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

class CampaignPlan(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    LifecycleMixin,
    VersionMetadataMixin,
    Base,
):
    __tablename__ = "campaign_plans"

    __table_args__ = (
        UniqueConstraint(
            "campaign_id",
            "version",
            name="uq_campaign_plans_campaign_version",
        ),
    )

    campaign_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    strategy_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("strategies.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    parent_version_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("campaign_plans.id", ondelete="SET NULL"),
        nullable=True,
    )

class ChannelPlan(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    ProvenanceMixin,
    Base,
):
    __tablename__ = "channel_plans"

    __table_args__ = (
        UniqueConstraint(
            "campaign_plan_id",
            "channel",
            name="uq_channel_plans_campaign_plan_channel",
        ),
    )

    campaign_plan_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("campaign_plans.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    channel: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

class ContentItem(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    ProvenanceMixin,
    Base,
):
    __tablename__ = "content_items"

    channel_plan_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("channel_plans.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    content_kind: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    working_title: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )