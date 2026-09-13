from modules.performance_learning.models import PerformanceRecord

from sqlalchemy import UniqueConstraint
from modules.common.enums import SourceType
from modules.performance_learning.models import (
    PerformanceFinding,
    PerformanceFindingMetric,
    PerformanceMetric,
    PerformanceRecord,
)
def test_performance_record_table_contract():
    columns = PerformanceRecord.__table__.columns

    assert set(columns.keys()) == {
        "id",
        "publication_id",
        "captured_at",
        "window_start_at",
        "window_end_at",
        "source_key",
        "external_record_id",
        "created_at",
        "updated_at",
    }

    assert columns["publication_id"].nullable is False
    assert columns["captured_at"].nullable is False
    assert columns["window_start_at"].nullable is True
    assert columns["window_end_at"].nullable is True
    assert columns["source_key"].nullable is True
    assert columns["external_record_id"].nullable is True

    publication_fk = next(
        iter(columns["publication_id"].foreign_keys)
    )

    assert publication_fk.target_fullname == "publications.id"
    assert publication_fk.ondelete == "RESTRICT"

    assert columns["captured_at"].type.timezone is True
    assert columns["window_start_at"].type.timezone is True
    assert columns["window_end_at"].type.timezone is True

    assert columns["source_key"].type.length == 128
    assert columns["external_record_id"].type.length == 255

    assert "source_type" not in columns
    assert "status" not in columns
    assert "version" not in columns
    assert "schema_version" not in columns
    assert "is_outdated" not in columns

def test_performance_metric_table_contract():
    columns = PerformanceMetric.__table__.columns

    assert set(columns.keys()) == {
        "id",
        "performance_record_id",
        "metric_key",
        "value",
        "unit",
        "created_at",
        "updated_at",
    }

    assert columns["performance_record_id"].nullable is False
    assert columns["metric_key"].nullable is False
    assert columns["value"].nullable is False
    assert columns["unit"].nullable is True

    performance_record_fk = next(
        iter(columns["performance_record_id"].foreign_keys)
    )

    assert (
        performance_record_fk.target_fullname
        == "performance_records.id"
    )
    assert performance_record_fk.ondelete == "CASCADE"

    assert columns["metric_key"].type.length == 64
    assert columns["value"].type.precision == 24
    assert columns["value"].type.scale == 6
    assert columns["unit"].type.length == 32

    assert "source_type" not in columns
    assert "status" not in columns
    assert "version" not in columns
    assert "schema_version" not in columns
    assert "is_outdated" not in columns


def test_performance_metric_unique_key_per_record():
    unique_constraints = {
        constraint.name: [
            column.name for column in constraint.columns
        ]
        for constraint
        in PerformanceMetric.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    }

    assert unique_constraints[
        "uq_performance_metrics_record_key"
    ] == [
        "performance_record_id",
        "metric_key",
    ]

def test_performance_finding_table_contract():
    columns = PerformanceFinding.__table__.columns

    assert set(columns.keys()) == {
        "id",
        "publication_id",
        "finding_kind",
        "statement",
        "rationale",
        "source_type",
        "created_at",
        "updated_at",
    }

    assert columns["publication_id"].nullable is False
    assert columns["finding_kind"].nullable is False
    assert columns["statement"].nullable is False
    assert columns["rationale"].nullable is True
    assert columns["source_type"].nullable is False

    publication_fk = next(
        iter(columns["publication_id"].foreign_keys)
    )

    assert publication_fk.target_fullname == "publications.id"
    assert publication_fk.ondelete == "RESTRICT"

    assert columns["finding_kind"].type.length == 64
    assert columns["source_type"].type.enum_class is SourceType
    assert columns["source_type"].type.length == 32

    assert "status" not in columns
    assert "version" not in columns
    assert "schema_version" not in columns
    assert "is_outdated" not in columns

def test_performance_finding_metric_table_contract():
    columns = PerformanceFindingMetric.__table__.columns

    assert set(columns.keys()) == {
        "id",
        "performance_finding_id",
        "performance_metric_id",
        "created_at",
        "updated_at",
    }

    assert columns["performance_finding_id"].nullable is False
    assert columns["performance_metric_id"].nullable is False

    finding_fk = next(
        iter(columns["performance_finding_id"].foreign_keys)
    )
    metric_fk = next(
        iter(columns["performance_metric_id"].foreign_keys)
    )

    assert (
        finding_fk.target_fullname
        == "performance_findings.id"
    )
    assert finding_fk.ondelete == "CASCADE"

    assert (
        metric_fk.target_fullname
        == "performance_metrics.id"
    )
    assert metric_fk.ondelete == "RESTRICT"

    assert "source_type" not in columns
    assert "status" not in columns
    assert "version" not in columns
    assert "schema_version" not in columns
    assert "is_outdated" not in columns


def test_performance_finding_metric_unique_pair():
    unique_constraints = {
        constraint.name: [
            column.name for column in constraint.columns
        ]
        for constraint
        in PerformanceFindingMetric.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    }

    assert unique_constraints[
        "uq_performance_finding_metrics_pair"
    ] == [
        "performance_finding_id",
        "performance_metric_id",
    ]