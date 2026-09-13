import uuid
from datetime import datetime, timedelta, timezone

import pytest
from decimal import Decimal

from modules.performance_learning.models import PerformanceRecord

from modules.performance_learning.services import (
    PerformanceLearningInvariantError,
    build_performance_record,
    build_performance_metric,
)
from modules.qa_approval_activation.enums import PublicationStatus
from modules.qa_approval_activation.models import Publication


def build_published_publication(
    *,
    published_at: datetime | None = None,
) -> Publication:
    return Publication(
        id=uuid.uuid4(),
        final_asset_id=uuid.uuid4(),
        approval_id=uuid.uuid4(),
        channel="TIKTOK",
        status=PublicationStatus.PUBLISHED,
        published_at=published_at
        or datetime(2026, 9, 13, 12, 0, tzinfo=timezone.utc),
    )


def test_build_performance_record_for_published_publication():
    published_at = datetime(
        2026,
        9,
        13,
        12,
        0,
        tzinfo=timezone.utc,
    )
    captured_at = published_at + timedelta(hours=2)

    publication = build_published_publication(
        published_at=published_at,
    )

    record = build_performance_record(
        publication=publication,
        captured_at=captured_at,
        window_start_at=published_at,
        window_end_at=captured_at,
        source_key="tiktok-api",
        external_record_id="snapshot-123",
    )

    assert record.publication_id == publication.id
    assert record.captured_at == captured_at
    assert record.window_start_at == published_at
    assert record.window_end_at == captured_at
    assert record.source_key == "tiktok-api"
    assert record.external_record_id == "snapshot-123"


def test_performance_record_requires_published_publication():
    publication = Publication(
        id=uuid.uuid4(),
        final_asset_id=uuid.uuid4(),
        approval_id=uuid.uuid4(),
        channel="TIKTOK",
        status=PublicationStatus.PUBLISHING,
    )

    with pytest.raises(
        PerformanceLearningInvariantError,
        match="Performance data requires a PUBLISHED Publication.",
    ):
        build_performance_record(
            publication=publication,
            captured_at=datetime.now(timezone.utc),
        )


def test_published_publication_requires_published_at():
    publication = Publication(
        id=uuid.uuid4(),
        final_asset_id=uuid.uuid4(),
        approval_id=uuid.uuid4(),
        channel="TIKTOK",
        status=PublicationStatus.PUBLISHED,
        published_at=None,
    )

    with pytest.raises(
        PerformanceLearningInvariantError,
        match="Published Publication must have published_at.",
    ):
        build_performance_record(
            publication=publication,
            captured_at=datetime.now(timezone.utc),
        )


def test_performance_window_requires_both_boundaries():
    publication = build_published_publication()

    with pytest.raises(
        PerformanceLearningInvariantError,
        match="Performance window requires both start and end timestamps.",
    ):
        build_performance_record(
            publication=publication,
            captured_at=publication.published_at + timedelta(hours=2),
            window_start_at=publication.published_at,
        )


def test_performance_window_end_cannot_precede_start():
    publication = build_published_publication()

    with pytest.raises(
        PerformanceLearningInvariantError,
        match="Performance window end cannot be before its start.",
    ):
        build_performance_record(
            publication=publication,
            captured_at=publication.published_at + timedelta(hours=2),
            window_start_at=publication.published_at + timedelta(hours=1),
            window_end_at=publication.published_at,
        )


def test_performance_cannot_be_captured_before_publication():
    publication = build_published_publication()

    with pytest.raises(
        PerformanceLearningInvariantError,
        match="Performance data cannot be captured before publication.",
    ):
        build_performance_record(
            publication=publication,
            captured_at=publication.published_at - timedelta(minutes=1),
        )


def test_performance_window_cannot_end_after_capture():
    publication = build_published_publication()
    captured_at = publication.published_at + timedelta(hours=1)

    with pytest.raises(
        PerformanceLearningInvariantError,
        match="Performance window cannot end after captured_at.",
    ):
        build_performance_record(
            publication=publication,
            captured_at=captured_at,
            window_start_at=publication.published_at,
            window_end_at=captured_at + timedelta(minutes=1),
        )

def test_build_performance_metric():
    record = PerformanceRecord(
        id=uuid.uuid4(),
        publication_id=uuid.uuid4(),
        captured_at=datetime.now(timezone.utc),
    )

    metric = build_performance_metric(
        performance_record=record,
        metric_key="  net_follower_change  ",
        value=Decimal("-3.25"),
        unit="  count  ",
    )

    assert metric.performance_record_id == record.id
    assert metric.metric_key == "net_follower_change"
    assert metric.value == Decimal("-3.25")
    assert metric.unit == "count"


def test_performance_metric_blank_unit_becomes_none():
    record = PerformanceRecord(
        id=uuid.uuid4(),
        publication_id=uuid.uuid4(),
        captured_at=datetime.now(timezone.utc),
    )

    metric = build_performance_metric(
        performance_record=record,
        metric_key="views",
        value=Decimal("100"),
        unit="   ",
    )

    assert metric.unit is None


def test_performance_metric_key_cannot_be_empty():
    record = PerformanceRecord(
        id=uuid.uuid4(),
        publication_id=uuid.uuid4(),
        captured_at=datetime.now(timezone.utc),
    )

    with pytest.raises(
        PerformanceLearningInvariantError,
        match="Performance metric key cannot be empty.",
    ):
        build_performance_metric(
            performance_record=record,
            metric_key="   ",
            value=Decimal("1"),
        )


def test_performance_metric_value_must_be_finite():
    record = PerformanceRecord(
        id=uuid.uuid4(),
        publication_id=uuid.uuid4(),
        captured_at=datetime.now(timezone.utc),
    )

    with pytest.raises(
        PerformanceLearningInvariantError,
        match="Performance metric value must be finite.",
    ):
        build_performance_metric(
            performance_record=record,
            metric_key="views",
            value=Decimal("NaN"),
        )


def test_performance_metric_requires_persisted_record():
    record = PerformanceRecord(
        publication_id=uuid.uuid4(),
        captured_at=datetime.now(timezone.utc),
    )

    with pytest.raises(
        PerformanceLearningInvariantError,
        match="PerformanceMetric requires a persisted PerformanceRecord.",
    ):
        build_performance_metric(
            performance_record=record,
            metric_key="views",
            value=Decimal("100"),
        )