import uuid
from datetime import datetime, timezone

import pytest

from modules.qa_approval_activation.enums import (
    ApprovalStatus,
    PublicationStatus,
    QualityReviewStatus,
)
from modules.qa_approval_activation.models import (
    Approval,
    Publication,
    QualityReview,
)
from modules.qa_approval_activation.services import (
    ApprovalInvariantError,
    cancel_approval,
    review_approval,
    QualityReviewInvariantError,
    transition_quality_review,
    build_publication,
    ensure_publication_is_approved_for_final_asset,
    PublicationInvariantError,
    transition_publication,
)
from modules.content_production.models import FinalAsset

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

def test_quality_review_transitions_pending_to_running():
    started_at = datetime(
        2026,
        9,
        13,
        19,
        0,
        tzinfo=timezone.utc,
    )

    quality_review = QualityReview(
        final_asset_id=uuid.uuid4(),
        status=QualityReviewStatus.PENDING,
    )

    result = transition_quality_review(
        quality_review=quality_review,
        target_status=QualityReviewStatus.RUNNING,
        transitioned_at=started_at,
    )

    assert result is quality_review
    assert quality_review.status == QualityReviewStatus.RUNNING
    assert quality_review.started_at == started_at
    assert quality_review.finished_at is None
    assert quality_review.error_message is None


def test_quality_review_transitions_running_to_terminal_outcomes():
    started_at = datetime(
        2026,
        9,
        13,
        19,
        0,
        tzinfo=timezone.utc,
    )
    finished_at = datetime(
        2026,
        9,
        13,
        19,
        5,
        tzinfo=timezone.utc,
    )

    for target_status in (
        QualityReviewStatus.PASSED,
        QualityReviewStatus.NEEDS_REVIEW,
        QualityReviewStatus.CANCELLED,
    ):
        quality_review = QualityReview(
            final_asset_id=uuid.uuid4(),
            status=QualityReviewStatus.RUNNING,
            started_at=started_at,
        )

        transition_quality_review(
            quality_review=quality_review,
            target_status=target_status,
            transitioned_at=finished_at,
        )

        assert quality_review.status == target_status
        assert quality_review.started_at == started_at
        assert quality_review.finished_at == finished_at
        assert quality_review.error_message is None


def test_quality_review_failed_records_error_message():
    started_at = datetime(
        2026,
        9,
        13,
        19,
        0,
        tzinfo=timezone.utc,
    )
    finished_at = datetime(
        2026,
        9,
        13,
        19,
        5,
        tzinfo=timezone.utc,
    )

    quality_review = QualityReview(
        final_asset_id=uuid.uuid4(),
        status=QualityReviewStatus.RUNNING,
        started_at=started_at,
    )

    transition_quality_review(
        quality_review=quality_review,
        target_status=QualityReviewStatus.FAILED,
        transitioned_at=finished_at,
        error_message="quality check execution failed",
    )

    assert quality_review.status == QualityReviewStatus.FAILED
    assert quality_review.finished_at == finished_at
    assert (
        quality_review.error_message
        == "quality check execution failed"
    )


def test_quality_review_can_cancel_while_pending():
    cancelled_at = datetime(
        2026,
        9,
        13,
        19,
        0,
        tzinfo=timezone.utc,
    )

    quality_review = QualityReview(
        final_asset_id=uuid.uuid4(),
        status=QualityReviewStatus.PENDING,
    )

    transition_quality_review(
        quality_review=quality_review,
        target_status=QualityReviewStatus.CANCELLED,
        transitioned_at=cancelled_at,
    )

    assert quality_review.status == QualityReviewStatus.CANCELLED
    assert quality_review.started_at is None
    assert quality_review.finished_at == cancelled_at


def test_quality_review_rejects_invalid_transition():
    quality_review = QualityReview(
        final_asset_id=uuid.uuid4(),
        status=QualityReviewStatus.PENDING,
    )

    with pytest.raises(
        QualityReviewInvariantError,
        match="QualityReview cannot transition from PENDING to PASSED.",
    ):
        transition_quality_review(
            quality_review=quality_review,
            target_status=QualityReviewStatus.PASSED,
        )


def test_quality_review_rejects_transition_from_terminal_status():
    quality_review = QualityReview(
        final_asset_id=uuid.uuid4(),
        status=QualityReviewStatus.PASSED,
    )

    with pytest.raises(
        QualityReviewInvariantError,
        match="QualityReview cannot transition from PASSED to RUNNING.",
    ):
        transition_quality_review(
            quality_review=quality_review,
            target_status=QualityReviewStatus.RUNNING,
        )


def test_quality_review_rejects_finish_before_start():
    started_at = datetime(
        2026,
        9,
        13,
        19,
        5,
        tzinfo=timezone.utc,
    )
    finished_at = datetime(
        2026,
        9,
        13,
        19,
        0,
        tzinfo=timezone.utc,
    )

    quality_review = QualityReview(
        final_asset_id=uuid.uuid4(),
        status=QualityReviewStatus.RUNNING,
        started_at=started_at,
    )

    with pytest.raises(
        QualityReviewInvariantError,
        match=(
            "QualityReview finished_at cannot be earlier than started_at."
        ),
    ):
        transition_quality_review(
            quality_review=quality_review,
            target_status=QualityReviewStatus.PASSED,
            transitioned_at=finished_at,
        )

def test_publication_invariant_accepts_approved_matching_final_asset():
    final_asset = FinalAsset(
        id=uuid.uuid4(),
        production_run_id=uuid.uuid4(),
        output_key="master",
        asset_kind="VIDEO",
        storage_uri="storage://final/master.mp4",
    )

    approval = Approval(
        id=uuid.uuid4(),
        final_asset_id=final_asset.id,
        status=ApprovalStatus.APPROVED,
    )

    ensure_publication_is_approved_for_final_asset(
        final_asset=final_asset,
        approval=approval,
    )


def test_publication_invariant_rejects_approval_for_other_final_asset():
    final_asset = FinalAsset(
        id=uuid.uuid4(),
        production_run_id=uuid.uuid4(),
        output_key="master",
        asset_kind="VIDEO",
        storage_uri="storage://final/master.mp4",
    )

    approval = Approval(
        id=uuid.uuid4(),
        final_asset_id=uuid.uuid4(),
        status=ApprovalStatus.APPROVED,
    )

    with pytest.raises(
        ApprovalInvariantError,
        match="Approval must belong to the FinalAsset being published.",
    ):
        ensure_publication_is_approved_for_final_asset(
            final_asset=final_asset,
            approval=approval,
        )


def test_publication_invariant_requires_approved_status():
    final_asset = FinalAsset(
        id=uuid.uuid4(),
        production_run_id=uuid.uuid4(),
        output_key="master",
        asset_kind="VIDEO",
        storage_uri="storage://final/master.mp4",
    )

    approval = Approval(
        id=uuid.uuid4(),
        final_asset_id=final_asset.id,
        status=ApprovalStatus.PENDING,
    )

    with pytest.raises(
        ApprovalInvariantError,
        match="Publication requires an APPROVED Approval.",
    ):
        ensure_publication_is_approved_for_final_asset(
            final_asset=final_asset,
            approval=approval,
        )


def test_build_publication():
    final_asset = FinalAsset(
        id=uuid.uuid4(),
        production_run_id=uuid.uuid4(),
        output_key="master",
        asset_kind="VIDEO",
        storage_uri="storage://final/master.mp4",
    )

    approval = Approval(
        id=uuid.uuid4(),
        final_asset_id=final_asset.id,
        status=ApprovalStatus.APPROVED,
    )

    publication = build_publication(
        final_asset=final_asset,
        approval=approval,
        channel="TIKTOK",
        provider_key="tiktok-api",
    )

    assert isinstance(publication, Publication)
    assert publication.final_asset_id == final_asset.id
    assert publication.approval_id == approval.id
    assert publication.channel == "TIKTOK"
    assert publication.provider_key == "tiktok-api"

def test_publication_transitions_pending_to_publishing():
    publication = Publication(
        final_asset_id=uuid.uuid4(),
        approval_id=uuid.uuid4(),
        channel="TIKTOK",
        status=PublicationStatus.PENDING,
    )

    result = transition_publication(
        publication=publication,
        target_status=PublicationStatus.PUBLISHING,
    )

    assert result is publication
    assert publication.status == PublicationStatus.PUBLISHING


def test_publication_transitions_publishing_to_published():
    published_at = datetime(
        2026,
        9,
        13,
        19,
        30,
        tzinfo=timezone.utc,
    )

    publication = Publication(
        final_asset_id=uuid.uuid4(),
        approval_id=uuid.uuid4(),
        channel="TIKTOK",
        status=PublicationStatus.PUBLISHING,
    )

    transition_publication(
        publication=publication,
        target_status=PublicationStatus.PUBLISHED,
        transitioned_at=published_at,
        external_publication_id="video-123",
        published_url="https://example.com/video-123",
    )

    assert publication.status == PublicationStatus.PUBLISHED
    assert publication.external_publication_id == "video-123"
    assert publication.published_url == "https://example.com/video-123"
    assert publication.published_at == published_at
    assert publication.error_message is None


def test_publication_failed_records_error_message():
    publication = Publication(
        final_asset_id=uuid.uuid4(),
        approval_id=uuid.uuid4(),
        channel="TIKTOK",
        status=PublicationStatus.PUBLISHING,
    )

    transition_publication(
        publication=publication,
        target_status=PublicationStatus.FAILED,
        error_message="provider rejected publication",
    )

    assert publication.status == PublicationStatus.FAILED
    assert (
        publication.error_message
        == "provider rejected publication"
    )


def test_publication_can_cancel_while_pending():
    publication = Publication(
        final_asset_id=uuid.uuid4(),
        approval_id=uuid.uuid4(),
        channel="TIKTOK",
        status=PublicationStatus.PENDING,
    )

    transition_publication(
        publication=publication,
        target_status=PublicationStatus.CANCELLED,
    )

    assert publication.status == PublicationStatus.CANCELLED
    assert publication.error_message is None


def test_publication_can_cancel_while_publishing():
    publication = Publication(
        final_asset_id=uuid.uuid4(),
        approval_id=uuid.uuid4(),
        channel="TIKTOK",
        status=PublicationStatus.PUBLISHING,
    )

    transition_publication(
        publication=publication,
        target_status=PublicationStatus.CANCELLED,
    )

    assert publication.status == PublicationStatus.CANCELLED


def test_publication_rejects_invalid_transition():
    publication = Publication(
        final_asset_id=uuid.uuid4(),
        approval_id=uuid.uuid4(),
        channel="TIKTOK",
        status=PublicationStatus.PENDING,
    )

    with pytest.raises(
        PublicationInvariantError,
        match="Publication cannot transition from PENDING to PUBLISHED.",
    ):
        transition_publication(
            publication=publication,
            target_status=PublicationStatus.PUBLISHED,
        )


def test_publication_rejects_transition_from_terminal_status():
    publication = Publication(
        final_asset_id=uuid.uuid4(),
        approval_id=uuid.uuid4(),
        channel="TIKTOK",
        status=PublicationStatus.PUBLISHED,
    )

    with pytest.raises(
        PublicationInvariantError,
        match="Publication cannot transition from PUBLISHED to PUBLISHING.",
    ):
        transition_publication(
            publication=publication,
            target_status=PublicationStatus.PUBLISHING,
        )