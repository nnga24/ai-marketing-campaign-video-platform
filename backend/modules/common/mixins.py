import uuid
from datetime import datetime

from sqlalchemy import DateTime, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, Enum as SAEnum, Uuid, func
from modules.common.enums import EntityStatus, SourceType


class UUIDPrimaryKeyMixin:
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class LifecycleMixin:
    status: Mapped[EntityStatus] = mapped_column(
        SAEnum(
            EntityStatus,
            native_enum=False,
            length=32,
        ),
        nullable=False,
        default=EntityStatus.DRAFT,
        server_default=EntityStatus.DRAFT.value,
    )


class ProvenanceMixin:
    source_type: Mapped[SourceType] = mapped_column(
        SAEnum(
            SourceType,
            native_enum=False,
            length=32,
        ),
        nullable=False,
    )