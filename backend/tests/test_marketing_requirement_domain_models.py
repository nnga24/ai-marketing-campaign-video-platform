from sqlalchemy import UniqueConstraint

from modules.marketing_requirement.models import (
    MarketingBrief,
    MarketingRequirement,
)
from modules.common.enums import SourceType
from modules.marketing_requirement.enums import (
    MarketingDecisionStatus,
    MarketingRequirementType,
)


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


def test_marketing_requirement_table_contract():
    columns = MarketingRequirement.__table__.columns

    assert set(columns.keys()) == {
        "id",
        "marketing_brief_id",
        "requirement_type",
        "statement",
        "decision_status",
        "created_at",
        "updated_at",
        "source_type",
    }

    assert columns["marketing_brief_id"].nullable is False
    assert columns["requirement_type"].nullable is False
    assert columns["statement"].nullable is False
    assert columns["decision_status"].nullable is False
    assert columns["source_type"].nullable is False

    brief_fk = next(iter(columns["marketing_brief_id"].foreign_keys))

    assert brief_fk.target_fullname == "marketing_briefs.id"
    assert brief_fk.ondelete == "CASCADE"

    assert "version" not in columns
    assert "status" not in columns
    assert "schema_version" not in columns
    assert "is_outdated" not in columns


def test_marketing_requirement_enum_contract():
    columns = MarketingRequirement.__table__.columns

    assert columns["requirement_type"].type.enum_class is MarketingRequirementType
    assert columns["decision_status"].type.enum_class is MarketingDecisionStatus
    assert columns["source_type"].type.enum_class is SourceType


def test_marketing_requirement_requires_explicit_source_and_decision_status():
    columns = MarketingRequirement.__table__.columns

    assert columns["source_type"].default is None
    assert columns["source_type"].server_default is None

    assert columns["decision_status"].default is None
    assert columns["decision_status"].server_default is None

    assert columns["requirement_type"].default is None
    assert columns["requirement_type"].server_default is None