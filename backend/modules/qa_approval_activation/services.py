import uuid
from datetime import datetime, timezone

from modules.qa_approval_activation.enums import ApprovalStatus
from modules.qa_approval_activation.models import Approval


class ApprovalInvariantError(ValueError):
    pass


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