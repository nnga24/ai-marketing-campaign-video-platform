import uuid

from modules.brand_intelligence.models import BrandProfile, ProductTruth
from modules.common.enums import SourceType

class BrandIntelligenceInvariantError(ValueError):
    pass


def ensure_brand_profile_parent_matches_brand(
    *,
    brand_id: uuid.UUID,
    parent: BrandProfile | None,
) -> None:
    if parent is not None and parent.brand_id != brand_id:
        raise BrandIntelligenceInvariantError(
            "BrandProfile parent must belong to the same brand."
        )


def ensure_product_truth_parent_matches_product(
    *,
    product_id: uuid.UUID,
    parent: ProductTruth | None,
) -> None:
    if parent is not None and parent.product_id != product_id:
        raise BrandIntelligenceInvariantError(
            "ProductTruth parent must belong to the same product."
        )


def build_brand_profile_version(
    *,
    brand_id: uuid.UUID,
    source_type: SourceType,
    overview: str | None = None,
    parent: BrandProfile | None = None,
) -> BrandProfile:
    ensure_brand_profile_parent_matches_brand(
        brand_id=brand_id,
        parent=parent,
    )

    return BrandProfile(
        brand_id=brand_id,
        parent_version_id=parent.id if parent is not None else None,
        version=parent.version + 1 if parent is not None else 1,
        source_type=source_type,
        overview=overview,
    )


def build_product_truth_version(
    *,
    product_id: uuid.UUID,
    parent: ProductTruth | None = None,
) -> ProductTruth:
    ensure_product_truth_parent_matches_product(
        product_id=product_id,
        parent=parent,
    )

    return ProductTruth(
        product_id=product_id,
        parent_version_id=parent.id if parent is not None else None,
        version=parent.version + 1 if parent is not None else 1,
    )