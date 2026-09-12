import uuid

from sqlalchemy import (
    Enum as SAEnum,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)

from modules.brand_intelligence.enums import (
    FactVerificationStatus,
    ProductFactType,
)
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database.base import Base
from modules.common.mixins import (
    LifecycleMixin,
    ProvenanceMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
    VersionedArtifactMixin,
    VersionMetadataMixin,
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

class Product(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    LifecycleMixin,
    Base,
):
    __tablename__ = "products"

    __table_args__ = (
        UniqueConstraint(
            "brand_id",
            "slug",
            name="uq_products_brand_slug",
        ),
    )

    brand_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("brands.id", ondelete="CASCADE"),
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

class ProductTruth(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    LifecycleMixin,
    VersionMetadataMixin,
    Base,
):
    __tablename__ = "product_truths"

    __table_args__ = (
        UniqueConstraint(
            "product_id",
            "version",
            name="uq_product_truths_product_version",
        ),
    )

    product_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    parent_version_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("product_truths.id", ondelete="SET NULL"),
        nullable=True,
    )

class ProductFact(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    ProvenanceMixin,
    Base,
):
    __tablename__ = "product_facts"

    product_truth_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("product_truths.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    fact_type: Mapped[ProductFactType] = mapped_column(
        SAEnum(
            ProductFactType,
            native_enum=False,
            length=32,
        ),
        nullable=False,
    )

    statement: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    verification_status: Mapped[FactVerificationStatus] = mapped_column(
        SAEnum(
            FactVerificationStatus,
            native_enum=False,
            length=32,
        ),
        nullable=False,
    )

class ProductClaim(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    ProvenanceMixin,
    Base,
):
    __tablename__ = "product_claims"

    product_truth_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("product_truths.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    statement: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    verification_status: Mapped[FactVerificationStatus] = mapped_column(
        SAEnum(
            FactVerificationStatus,
            native_enum=False,
            length=32,
        ),
        nullable=False,
    )


class ProductClaimEvidence(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    ProvenanceMixin,
    Base,
):
    __tablename__ = "product_claim_evidence"

    product_claim_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("product_claims.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    reference_uri: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    verification_status: Mapped[FactVerificationStatus] = mapped_column(
        SAEnum(
            FactVerificationStatus,
            native_enum=False,
            length=32,
        ),
        nullable=False,
    )