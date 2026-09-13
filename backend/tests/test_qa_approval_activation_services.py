import uuid
from datetime import datetime, timezone

import pytest

from modules.qa_approval_activation.enums import ApprovalStatus
from modules.qa_approval_activation.models import Approval
from modules.qa_approval_activation.services import (
    ApprovalInvariantError,
    cancel_approval,
    review_approval,
)


def test_review_approval_accepts_review_decisions():
    reviewer_id = uuid.uuid4()
    reviewed_at = datetime(
        2026,
        9,
        13,
        18,
        45,
        tzinfo=timezone.utc,
    )

    for decision in (
        ApprovalStatus.APPROVED,
        ApprovalStatus.CHANGES_REQUESTED,
        ApprovalStatus.REJECTED,
    ):
        approval = Approval(
            final_asset_id=uuid.uuid4(),
            status=ApprovalStatus.PENDING,
        )

        result = review_approval(
            approval=approval,
            decision=decision,
            reviewed_by_user_id=reviewer_id,
            review_note="reviewed",
            reviewed_at=reviewed_at,
        )

        assert result is approval
        assert approval.status == decision
        assert approval.reviewed_by_user_id == reviewer_id
        assert approval.review_note == "reviewed"
        assert approval.reviewed_at == reviewed_at


def test_review_approval_requires_pending_status():
    approval = Approval(
        final_asset_id=uuid.uuid4(),
        status=ApprovalStatus.APPROVED,
    )

    with pytest.raises(
        ApprovalInvariantError,
        match="Only a pending Approval can be reviewed.",
    ):
        review_approval(
            approval=approval,
            decision=ApprovalStatus.REJECTED,
            reviewed_by_user_id=uuid.uuid4(),
        )


def test_review_approval_rejects_non_review_decision():
    approval = Approval(
        final_asset_id=uuid.uuid4(),
        status=ApprovalStatus.PENDING,
    )

    with pytest.raises(
        ApprovalInvariantError,
        match=(
            "Approval review decision must be APPROVED, "
            "CHANGES_REQUESTED, or REJECTED."
        ),
    ):
        review_approval(
            approval=approval,
            decision=ApprovalStatus.CANCELLED,
            reviewed_by_user_id=uuid.uuid4(),
        )


def test_cancel_approval_accepts_pending_status():
    approval = Approval(
        final_asset_id=uuid.uuid4(),
        status=ApprovalStatus.PENDING,
    )

    result = cancel_approval(
        approval=approval,
    )

    assert result is approval
    assert approval.status == ApprovalStatus.CANCELLED


def test_cancel_approval_requires_pending_status():
    approval = Approval(
        final_asset_id=uuid.uuid4(),
        status=ApprovalStatus.REJECTED,
    )

    with pytest.raises(
        ApprovalInvariantError,
        match="Only a pending Approval can be cancelled.",
    ):
        cancel_approval(
            approval=approval,
        )