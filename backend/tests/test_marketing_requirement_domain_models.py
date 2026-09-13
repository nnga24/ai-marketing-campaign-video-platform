from sqlalchemy import UniqueConstraint

from modules.marketing_requirement.models import MarketingBrief


def test_marketing_brief_table_contract():
    columns = MarketingBrief.__table__.columns

    assert set(columns.keys()) == {
        "id",
        "project_id",
        "parent_version_id",
        "created_at",
        "updated_at",
        "status",
        "version",
        "schema_version",
        "is_outdated",
    }

    assert columns["project_id"].nullable is False
    assert columns["parent_version_id"].nullable is True
    assert columns["status"].nullable is False
    assert columns["version"].nullable is False
    assert columns["schema_version"].nullable is False
    assert columns["is_outdated"].nullable is False

    project_fk = next(iter(columns["project_id"].foreign_keys))
    parent_fk = next(iter(columns["parent_version_id"].foreign_keys))

    assert project_fk.target_fullname == "projects.id"
    assert project_fk.ondelete == "CASCADE"

    assert parent_fk.target_fullname == "marketing_briefs.id"
    assert parent_fk.ondelete == "SET NULL"

    assert "source_type" not in columns


def test_marketing_brief_unique_version_per_project():
    unique_constraints = [
        constraint
        for constraint in MarketingBrief.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    ]

    matching_constraint = next(
        constraint
        for constraint in unique_constraints
        if constraint.name == "uq_marketing_briefs_project_version"
    )

    assert [column.name for column in matching_constraint.columns] == [
        "project_id",
        "version",
    ]