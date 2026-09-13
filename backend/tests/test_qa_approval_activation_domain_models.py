from modules.qa_approval_activation.enums import ApprovalStatus
from modules.qa_approval_activation.models import Approval


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