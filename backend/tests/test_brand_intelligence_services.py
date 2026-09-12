import uuid

import pytest
from modules.common.enums import SourceType
from modules.brand_intelligence.models import BrandProfile, ProductTruth
from modules.brand_intelligence.services import (
    BrandIntelligenceInvariantError,
    ensure_brand_profile_parent_matches_brand,
    ensure_product_truth_parent_matches_product,
    build_brand_profile_version,
    build_product_truth_version,
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

def test_build_brand_profile_first_version():
    brand_id = uuid.uuid4()

    profile = build_brand_profile_version(
        brand_id=brand_id,
        source_type=SourceType.USER_PROVIDED,
        overview="Local food brand.",
    )

    assert profile.brand_id == brand_id
    assert profile.version == 1
    assert profile.parent_version_id is None
    assert profile.source_type == SourceType.USER_PROVIDED
    assert profile.overview == "Local food brand."


def test_build_brand_profile_next_version():
    brand_id = uuid.uuid4()
    parent_id = uuid.uuid4()

    parent = BrandProfile(
        id=parent_id,
        brand_id=brand_id,
        version=2,
        source_type=SourceType.USER_PROVIDED,
    )

    profile = build_brand_profile_version(
        brand_id=brand_id,
        source_type=SourceType.AI_SUGGESTED,
        parent=parent,
    )

    assert profile.version == 3
    assert profile.parent_version_id == parent_id
    assert profile.source_type == SourceType.AI_SUGGESTED


def test_build_brand_profile_rejects_cross_brand_parent():
    parent = BrandProfile(
        id=uuid.uuid4(),
        brand_id=uuid.uuid4(),
        version=1,
        source_type=SourceType.USER_PROVIDED,
    )

    with pytest.raises(BrandIntelligenceInvariantError):
        build_brand_profile_version(
            brand_id=uuid.uuid4(),
            source_type=SourceType.USER_PROVIDED,
            parent=parent,
        )


def test_build_product_truth_first_version():
    product_id = uuid.uuid4()

    truth = build_product_truth_version(
        product_id=product_id,
    )

    assert truth.product_id == product_id
    assert truth.version == 1
    assert truth.parent_version_id is None


def test_build_product_truth_next_version():
    product_id = uuid.uuid4()
    parent_id = uuid.uuid4()

    parent = ProductTruth(
        id=parent_id,
        product_id=product_id,
        version=4,
    )

    truth = build_product_truth_version(
        product_id=product_id,
        parent=parent,
    )

    assert truth.version == 5
    assert truth.parent_version_id == parent_id


def test_build_product_truth_rejects_cross_product_parent():
    parent = ProductTruth(
        id=uuid.uuid4(),
        product_id=uuid.uuid4(),
        version=1,
    )

    with pytest.raises(BrandIntelligenceInvariantError):
        build_product_truth_version(
            product_id=uuid.uuid4(),
            parent=parent,
        )