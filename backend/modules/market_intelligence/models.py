import uuid
from datetime import datetime
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from modules.market_intelligence.enums import (
    ResearchRunStatus,
    ResearchTaskExecutionStatus,
)
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database.base import Base
from modules.common.mixins import (
    LifecycleMixin,
    ProvenanceMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
    VersionMetadataMixin,
)


class ResearchPlan(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    LifecycleMixin,
    VersionMetadataMixin,
    Base,
):
    __tablename__ = "research_plans"

    __table_args__ = (
        UniqueConstraint(
            "marketing_brief_id",
            "version",
            name="uq_research_plans_marketing_brief_version",
        ),
    )

    marketing_brief_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("marketing_briefs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    parent_version_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("research_plans.id", ondelete="SET NULL"),
        nullable=True,
    )

class ResearchTask(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    ProvenanceMixin,
    Base,
):
    __tablename__ = "research_tasks"

    __table_args__ = (
        UniqueConstraint(
            "research_plan_id",
            "position",
            name="uq_research_tasks_plan_position",
        ),
        CheckConstraint(
            "position >= 1",
            name="ck_research_tasks_position_positive",
        ),
    )

    research_plan_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("research_plans.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    position: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    objective: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

class ResearchRun(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "research_runs"

    research_plan_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("research_plans.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    status: Mapped[ResearchRunStatus] = mapped_column(
        SAEnum(
            ResearchRunStatus,
            native_enum=False,
            length=32,
        ),
        nullable=False,
        default=ResearchRunStatus.PENDING,
        server_default=ResearchRunStatus.PENDING.value,
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

class ResearchTaskExecution(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "research_task_executions"

    __table_args__ = (
        UniqueConstraint(
            "research_run_id",
            "research_task_id",
            name="uq_research_task_executions_run_task",
        ),
    )

    research_run_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("research_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    research_task_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("research_tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    status: Mapped[ResearchTaskExecutionStatus] = mapped_column(
        SAEnum(
            ResearchTaskExecutionStatus,
            native_enum=False,
            length=32,
        ),
        nullable=False,
        default=ResearchTaskExecutionStatus.PENDING,
        server_default=ResearchTaskExecutionStatus.PENDING.value,
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

class ResearchEvidence(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "research_evidence"

    __table_args__ = (
        UniqueConstraint(
            "research_task_execution_id",
            "content_fingerprint",
            name="uq_research_evidence_execution_fingerprint",
        ),
    )

    research_task_execution_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey(
            "research_task_executions.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    source_kind: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    provider_key: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
    )

    source_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    source_uri: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    source_external_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    title: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    content_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    content_fingerprint: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    retrieved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

class ResearchFinding(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    ProvenanceMixin,
    Base,
):
    __tablename__ = "research_findings"

    research_run_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("research_runs.id", ondelete="CASCADE"),
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