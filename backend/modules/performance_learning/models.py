import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import (
    DateTime,
    ForeignKey,
    String,
    Uuid,
    Numeric,
    UniqueConstraint,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database.base import Base
from modules.common.mixins import (
    ProvenanceMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


class PerformanceRecord(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "performance_records"

    publication_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("publications.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    captured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    window_start_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    window_end_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    source_key: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
    )

    external_record_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

class PerformanceMetric(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "performance_metrics"

    __table_args__ = (
        UniqueConstraint(
            "performance_record_id",
            "metric_key",
            name="uq_performance_metrics_record_key",
        ),
    )

    performance_record_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("performance_records.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    metric_key: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    value: Mapped[Decimal] = mapped_column(
        Numeric(24, 6),
        nullable=False,
    )

    unit: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
    )

class PerformanceFinding(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    ProvenanceMixin,
    Base,
):
    __tablename__ = "performance_findings"

    publication_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("publications.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    finding_kind: Mapped[str] = mapped_column(
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

class PerformanceFindingMetric(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "performance_finding_metrics"

    __table_args__ = (
        UniqueConstraint(
            "performance_finding_id",
            "performance_metric_id",
            name="uq_performance_finding_metrics_pair",
        ),
    )

    performance_finding_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("performance_findings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    performance_metric_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("performance_metrics.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )