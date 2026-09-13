import uuid
from datetime import datetime, timezone

from modules.qa_approval_activation.enums import (
    ApprovalStatus,
    QualityReviewStatus,
)
from modules.qa_approval_activation.models import (
    Approval,
    QualityReview,
)


class ApprovalInvariantError(ValueError):
    pass

class QualityReviewInvariantError(ValueError):
    pass


_QUALITY_REVIEW_TRANSITIONS = {
    QualityReviewStatus.PENDING: {
        QualityReviewStatus.RUNNING,
        QualityReviewStatus.CANCELLED,
    },
    QualityReviewStatus.RUNNING: {
        QualityReviewStatus.PASSED,
        QualityReviewStatus.FAILED,
        QualityReviewStatus.NEEDS_REVIEW,
        QualityReviewStatus.CANCELLED,
    },
    QualityReviewStatus.PASSED: set(),
    QualityReviewStatus.FAILED: set(),
    QualityReviewStatus.NEEDS_REVIEW: set(),
    QualityReviewStatus.CANCELLED: set(),
}

_REVIEW_DECISIONS = {
    ApprovalStatus.APPROVED,
    ApprovalStatus.CHANGES_REQUESTED,
    ApprovalStatus.REJECTED,
}


def review_approval(
    *,
    approval: Approval,
    decision: ApprovalStatus,
    reviewed_by_user_id: uuid.UUID,
    review_note: str | None = None,
    reviewed_at: datetime | None = None,
) -> Approval:
    if approval.status != ApprovalStatus.PENDING:
        raise ApprovalInvariantError(
            "Only a pending Approval can be reviewed."
        )

    if decision not in _REVIEW_DECISIONS:
        raise ApprovalInvariantError(
            "Approval review decision must be APPROVED, "
            "CHANGES_REQUESTED, or REJECTED."
        )

    approval.status = decision
    approval.reviewed_by_user_id = reviewed_by_user_id
    approval.review_note = review_note
    approval.reviewed_at = reviewed_at or datetime.now(timezone.utc)

    return approval


def cancel_approval(
    *,
    approval: Approval,
) -> Approval:
    if approval.status != ApprovalStatus.PENDING:
        raise ApprovalInvariantError(
            "Only a pending Approval can be cancelled."
        )

    approval.status = ApprovalStatus.CANCELLED

    return approval


def transition_quality_review(
    *,
    quality_review: QualityReview,
    target_status: QualityReviewStatus,
    transitioned_at: datetime | None = None,
    error_message: str | None = None,
) -> QualityReview:
    allowed_targets = _QUALITY_REVIEW_TRANSITIONS[
        quality_review.status
    ]

    if target_status not in allowed_targets:
        raise QualityReviewInvariantError(
            f"QualityReview cannot transition from "
            f"{quality_review.status.value} to {target_status.value}."
        )

    occurred_at = transitioned_at or datetime.now(timezone.utc)

    if target_status == QualityReviewStatus.RUNNING:
        quality_review.started_at = occurred_at

    else:
        if (
            quality_review.started_at is not None
            and occurred_at < quality_review.started_at
        ):
            raise QualityReviewInvariantError(
                "QualityReview finished_at cannot be earlier than started_at."
            )

        quality_review.finished_at = occurred_at

    quality_review.status = target_status

    if target_status == QualityReviewStatus.FAILED:
        quality_review.error_message = error_message
    else:
        quality_review.error_message = None

    return quality_review
