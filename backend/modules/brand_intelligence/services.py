import uuid

from modules.brand_intelligence.models import BrandProfile, ProductTruth


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