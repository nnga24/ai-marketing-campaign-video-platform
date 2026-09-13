import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Text,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database.base import Base
from modules.common.mixins import TimestampMixin, UUIDPrimaryKeyMixin
from modules.qa_approval_activation.enums import (
    ApprovalStatus,
    QualityReviewStatus,
)


class Approval(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "approvals"

    final_asset_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("final_assets.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    status: Mapped[ApprovalStatus] = mapped_column(
        SAEnum(
            ApprovalStatus,
            native_enum=False,
            length=32,
        ),
        nullable=False,
        default=ApprovalStatus.PENDING,
        server_default=ApprovalStatus.PENDING.value,
    )

    requested_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    reviewed_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    request_note: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    review_note: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

class QualityReview(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "quality_reviews"

    final_asset_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("final_assets.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    status: Mapped[QualityReviewStatus] = mapped_column(
        SAEnum(
            QualityReviewStatus,
            native_enum=False,
            length=32,
        ),
        nullable=False,
        default=QualityReviewStatus.PENDING,
        server_default=QualityReviewStatus.PENDING.value,
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