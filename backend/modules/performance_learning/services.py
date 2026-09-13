from datetime import datetime
from decimal import Decimal
from modules.performance_learning.models import (
    PerformanceFinding,
    PerformanceFindingMetric,
    PerformanceMetric,
    PerformanceRecord,
)
from modules.qa_approval_activation.enums import PublicationStatus
from modules.qa_approval_activation.models import Publication


class PerformanceLearningInvariantError(ValueError):
    pass


def ensure_publication_can_receive_performance_data(
    *,
    publication: Publication,
) -> None:
    if publication.status != PublicationStatus.PUBLISHED:
        raise PerformanceLearningInvariantError(
            "Performance data requires a PUBLISHED Publication."
        )

    if publication.published_at is None:
        raise PerformanceLearningInvariantError(
            "Published Publication must have published_at."
        )


def build_performance_record(
    *,
    publication: Publication,
    captured_at: datetime,
    window_start_at: datetime | None = None,
    window_end_at: datetime | None = None,
    source_key: str | None = None,
    external_record_id: str | None = None,
) -> PerformanceRecord:
    ensure_publication_can_receive_performance_data(
        publication=publication,
    )

    if (window_start_at is None) != (window_end_at is None):
        raise PerformanceLearningInvariantError(
            "Performance window requires both start and end timestamps."
        )

    if (
        window_start_at is not None
        and window_end_at is not None
        and window_end_at < window_start_at
    ):
        raise PerformanceLearningInvariantError(
            "Performance window end cannot be before its start."
        )

    if captured_at < publication.published_at:
        raise PerformanceLearningInvariantError(
            "Performance data cannot be captured before publication."
        )

    if (
        window_end_at is not None
        and window_end_at > captured_at
    ):
        raise PerformanceLearningInvariantError(
            "Performance window cannot end after captured_at."
        )

    return PerformanceRecord(
        publication_id=publication.id,
        captured_at=captured_at,
        window_start_at=window_start_at,
        window_end_at=window_end_at,
        source_key=source_key,
        external_record_id=external_record_id,
    )

def build_performance_metric(
    *,
    performance_record: PerformanceRecord,
    metric_key: str,
    value: Decimal,
    unit: str | None = None,
) -> PerformanceMetric:
    normalized_metric_key = metric_key.strip()

    if not normalized_metric_key:
        raise PerformanceLearningInvariantError(
            "Performance metric key cannot be empty."
        )

    if not value.is_finite():
        raise PerformanceLearningInvariantError(
            "Performance metric value must be finite."
        )

    if performance_record.id is None:
        raise PerformanceLearningInvariantError(
            "PerformanceMetric requires a persisted PerformanceRecord."
        )

    normalized_unit = unit.strip() if unit is not None else None

    if normalized_unit == "":
        normalized_unit = None

    return PerformanceMetric(
        performance_record_id=performance_record.id,
        metric_key=normalized_metric_key,
        value=value,
        unit=normalized_unit,
    )

def ensure_performance_finding_metric_lineage(
    *,
    performance_finding: PerformanceFinding,
    performance_metric: PerformanceMetric,
    performance_record: PerformanceRecord,
) -> None:
    if performance_finding.id is None:
        raise PerformanceLearningInvariantError(
            "PerformanceFinding must be persisted before linking metrics."
        )

    if performance_metric.id is None:
        raise PerformanceLearningInvariantError(
            "PerformanceMetric must be persisted before linking to a finding."
        )

    if performance_record.id is None:
        raise PerformanceLearningInvariantError(
            "PerformanceRecord must be persisted before linking findings."
        )

    if performance_metric.performance_record_id != performance_record.id:
        raise PerformanceLearningInvariantError(
            "PerformanceMetric must belong to the supplied PerformanceRecord."
        )

    if performance_finding.publication_id != performance_record.publication_id:
        raise PerformanceLearningInvariantError(
            "PerformanceFinding and PerformanceMetric must belong to the same Publication."
        )


def build_performance_finding_metric_link(
    *,
    performance_finding: PerformanceFinding,
    performance_metric: PerformanceMetric,
    performance_record: PerformanceRecord,
) -> PerformanceFindingMetric:
    ensure_performance_finding_metric_lineage(
        performance_finding=performance_finding,
        performance_metric=performance_metric,
        performance_record=performance_record,
    )

    return PerformanceFindingMetric(
        performance_finding_id=performance_finding.id,
        performance_metric_id=performance_metric.id,
    )