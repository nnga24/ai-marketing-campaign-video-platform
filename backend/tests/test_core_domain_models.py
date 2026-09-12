from sqlalchemy import UniqueConstraint

from modules.common.enums import EntityStatus
from modules.models import Project, Workspace


def test_workspace_table_contract():
    columns = Workspace.__table__.columns

    assert set(columns.keys()) == {
        "id",
        "name",
        "slug",
        "created_at",
        "updated_at",
    }

    assert columns["id"].primary_key is True
    assert columns["slug"].unique is True


def test_project_table_contract():
    columns = Project.__table__.columns

    assert set(columns.keys()) == {
        "id",
        "workspace_id",
        "name",
        "slug",
        "created_at",
        "updated_at",
        "status",
    }

    assert columns["id"].primary_key is True
    assert columns["workspace_id"].nullable is False

    workspace_fk = next(iter(columns["workspace_id"].foreign_keys))

    assert workspace_fk.target_fullname == "workspaces.id"
    assert workspace_fk.ondelete == "CASCADE"


def test_project_slug_is_unique_within_workspace():
    unique_constraints = [
        constraint
        for constraint in Project.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    ]

    assert any(
        constraint.name == "uq_projects_workspace_slug"
        and [column.name for column in constraint.columns]
        == ["workspace_id", "slug"]
        for constraint in unique_constraints
    )


def test_project_status_defaults_to_draft():
    status_column = Project.__table__.columns["status"]

    assert status_column.nullable is False
    assert status_column.default.arg == EntityStatus.DRAFT
    assert str(status_column.server_default.arg) == "DRAFT"