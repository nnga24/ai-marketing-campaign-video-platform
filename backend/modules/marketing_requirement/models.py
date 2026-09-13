import uuid

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database.base import Base
from modules.common.mixins import (
    LifecycleMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
    VersionMetadataMixin,
)

from modules.common.mixins import ProvenanceMixin
from modules.marketing_requirement.enums import (
    MarketingDecisionStatus,
    MarketingRequirementType,
)

class MarketingBrief(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    LifecycleMixin,
    VersionMetadataMixin,
    Base,
):
    __tablename__ = "marketing_briefs"

    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "version",
            name="uq_marketing_briefs_project_version",
        ),
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    parent_version_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("marketing_briefs.id", ondelete="SET NULL"),
        nullable=True,
    )

class MarketingRequirement(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    ProvenanceMixin,
    Base,
):
    __tablename__ = "marketing_requirements"

    marketing_brief_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("marketing_briefs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    requirement_type: Mapped[MarketingRequirementType] = mapped_column(
        SAEnum(
            MarketingRequirementType,
            native_enum=False,
            length=32,
        ),
        nullable=False,
    )

    statement: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    decision_status: Mapped[MarketingDecisionStatus] = mapped_column(
        SAEnum(
            MarketingDecisionStatus,
            native_enum=False,
            length=32,
        ),
        nullable=False,
    )