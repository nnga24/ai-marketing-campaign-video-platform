from sqlalchemy import UniqueConstraint

from modules.identity.enums import WorkspaceRole
from modules.identity.models import User, WorkspaceMembership


def test_user_table_contract():
    columns = User.__table__.columns

    assert set(columns.keys()) == {
        "id",
        "email",
        "display_name",
        "is_active",
        "created_at",
        "updated_at",
    }

    assert columns["id"].primary_key is True
    assert columns["email"].nullable is False
    assert columns["email"].unique is True
    assert columns["display_name"].nullable is True
    assert columns["is_active"].nullable is False


def test_workspace_membership_table_contract():
    columns = WorkspaceMembership.__table__.columns

    assert set(columns.keys()) == {
        "id",
        "workspace_id",
        "user_id",
        "role",
        "is_active",
        "created_at",
        "updated_at",
    }

    assert columns["workspace_id"].nullable is False
    assert columns["user_id"].nullable is False
    assert columns["role"].nullable is False

    workspace_fk = next(iter(columns["workspace_id"].foreign_keys))
    user_fk = next(iter(columns["user_id"].foreign_keys))

    assert workspace_fk.target_fullname == "workspaces.id"
    assert workspace_fk.ondelete == "CASCADE"

    assert user_fk.target_fullname == "users.id"
    assert user_fk.ondelete == "CASCADE"


def test_workspace_membership_is_unique_per_user_and_workspace():
    unique_constraints = [
        constraint
        for constraint in WorkspaceMembership.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    ]

    assert any(
        constraint.name == "uq_workspace_memberships_workspace_user"
        and [column.name for column in constraint.columns]
        == ["workspace_id", "user_id"]
        for constraint in unique_constraints
    )


def test_workspace_membership_defaults_to_member():
    role_column = WorkspaceMembership.__table__.columns["role"]

    assert role_column.default.arg == WorkspaceRole.MEMBER
    assert str(role_column.server_default.arg) == "MEMBER"