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


class Strategy(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    LifecycleMixin,
    VersionMetadataMixin,
    Base,
):
    __tablename__ = "strategies"

    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "version",
            name="uq_strategies_project_version",
        ),
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    research_run_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("research_runs.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    parent_version_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("strategies.id", ondelete="SET NULL"),
        nullable=True,
    )