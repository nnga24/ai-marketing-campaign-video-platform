import uuid

import pytest

from modules.brand_intelligence.models import BrandProfile, ProductTruth
from modules.brand_intelligence.services import (
    BrandIntelligenceInvariantError,
    ensure_brand_profile_parent_matches_brand,
    ensure_product_truth_parent_matches_product,
)


def test_brand_profile_parent_allows_same_brand():
    brand_id = uuid.uuid4()
    parent = BrandProfile(brand_id=brand_id)

    ensure_brand_profile_parent_matches_brand(
        brand_id=brand_id,
        parent=parent,
    )


def test_brand_profile_parent_rejects_different_brand():
    parent = BrandProfile(brand_id=uuid.uuid4())

    with pytest.raises(
        BrandIntelligenceInvariantError,
        match="same brand",
    ):
        ensure_brand_profile_parent_matches_brand(
            brand_id=uuid.uuid4(),
            parent=parent,
        )


def test_product_truth_parent_allows_same_product():
    product_id = uuid.uuid4()
    parent = ProductTruth(product_id=product_id)

    ensure_product_truth_parent_matches_product(
        product_id=product_id,
        parent=parent,
    )


def test_product_truth_parent_rejects_different_product():
    parent = ProductTruth(product_id=uuid.uuid4())

    with pytest.raises(
        BrandIntelligenceInvariantError,
        match="same product",
    ):
        ensure_product_truth_parent_matches_product(
            product_id=uuid.uuid4(),
            parent=parent,
        )