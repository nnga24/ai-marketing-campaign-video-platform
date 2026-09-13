from modules.qa_approval_activation.enums import (
    ApprovalStatus,
    QualityCheckOutcome,
    QualityReviewStatus,
)
from modules.qa_approval_activation.models import (
    Approval,
    QualityCheckResult,
    QualityReview,
)
from sqlalchemy import UniqueConstraint

def test_approval_table_contract():
    columns = Approval.__table__.columns

    assert set(columns.keys()) == {
        "id",
        "final_asset_id",
        "status",
        "requested_by_user_id",
        "reviewed_by_user_id",
        "request_note",
        "review_note",
        "reviewed_at",
        "created_at",
        "updated_at",
    }

    assert columns["final_asset_id"].nullable is False
    assert columns["status"].nullable is False
    assert columns["requested_by_user_id"].nullable is True
    assert columns["reviewed_by_user_id"].nullable is True
    assert columns["request_note"].nullable is True
    assert columns["review_note"].nullable is True
    assert columns["reviewed_at"].nullable is True

    final_asset_fk = next(
        iter(columns["final_asset_id"].foreign_keys)
    )
    requested_by_fk = next(
        iter(columns["requested_by_user_id"].foreign_keys)
    )
    reviewed_by_fk = next(
        iter(columns["reviewed_by_user_id"].foreign_keys)
    )

    assert final_asset_fk.target_fullname == "final_assets.id"
    assert final_asset_fk.ondelete == "RESTRICT"

    assert requested_by_fk.target_fullname == "users.id"
    assert requested_by_fk.ondelete == "RESTRICT"

    assert reviewed_by_fk.target_fullname == "users.id"
    assert reviewed_by_fk.ondelete == "RESTRICT"

    assert columns["status"].type.enum_class is ApprovalStatus
    assert columns["status"].type.length == 32
    assert columns["status"].server_default.arg == "PENDING"

    assert "source_type" not in columns
    assert "version" not in columns
    assert "schema_version" not in columns
    assert "is_outdated" not in columns

def test_quality_review_table_contract():
    columns = QualityReview.__table__.columns

    assert set(columns.keys()) == {
        "id",
        "final_asset_id",
        "status",
        "started_at",
        "finished_at",
        "error_message",
        "created_at",
        "updated_at",
    }

    assert columns["final_asset_id"].nullable is False
    assert columns["status"].nullable is False
    assert columns["started_at"].nullable is True
    assert columns["finished_at"].nullable is True
    assert columns["error_message"].nullable is True

    final_asset_fk = next(
        iter(columns["final_asset_id"].foreign_keys)
    )

    assert final_asset_fk.target_fullname == "final_assets.id"
    assert final_asset_fk.ondelete == "RESTRICT"

    assert columns["status"].type.enum_class is QualityReviewStatus
    assert columns["status"].type.length == 32
    assert columns["status"].server_default.arg == "PENDING"

    assert columns["started_at"].type.timezone is True
    assert columns["finished_at"].type.timezone is True

    assert "source_type" not in columns
    assert "version" not in columns
    assert "schema_version" not in columns
    assert "is_outdated" not in columns


def test_quality_check_result_table_contract():
    columns = QualityCheckResult.__table__.columns

    assert set(columns.keys()) == {
        "id",
        "quality_review_id",
        "check_key",
        "outcome",
        "summary",
        "created_at",
        "updated_at",
    }

    assert columns["quality_review_id"].nullable is False
    assert columns["check_key"].nullable is False
    assert columns["outcome"].nullable is False
    assert columns["summary"].nullable is True

    quality_review_fk = next(
        iter(columns["quality_review_id"].foreign_keys)
    )

    assert quality_review_fk.target_fullname == "quality_reviews.id"
    assert quality_review_fk.ondelete == "CASCADE"

    assert columns["check_key"].type.length == 64
    assert columns["outcome"].type.enum_class is QualityCheckOutcome
    assert columns["outcome"].type.length == 32

    assert "source_type" not in columns
    assert "status" not in columns
    assert "version" not in columns
    assert "schema_version" not in columns
    assert "is_outdated" not in columns


def test_quality_check_result_unique_key_per_review():
    unique_constraints = {
        constraint.name: [column.name for column in constraint.columns]
        for constraint in QualityCheckResult.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    }

    assert unique_constraints[
        "uq_quality_check_results_review_key"
    ] == [
        "quality_review_id",
        "check_key",
    ]