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

class StrategyDecision(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    ProvenanceMixin,
    Base,
):
    __tablename__ = "strategy_decisions"

    strategy_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("strategies.id", ondelete="CASCADE"),
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

class StrategyDecisionFinding(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "strategy_decision_findings"

    __table_args__ = (
        UniqueConstraint(
            "strategy_decision_id",
            "research_finding_id",
            name="uq_strategy_decision_finding_pair",
        ),
    )

    strategy_decision_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("strategy_decisions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    research_finding_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("research_findings.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )