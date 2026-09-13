from sqlalchemy import UniqueConstraint

from modules.market_intelligence.models import ResearchPlan


def test_research_plan_table_contract():
    columns = ResearchPlan.__table__.columns

    assert set(columns.keys()) == {
        "id",
        "marketing_brief_id",
        "parent_version_id",
        "created_at",
        "updated_at",
        "status",
        "version",
        "schema_version",
        "is_outdated",
    }

    assert columns["marketing_brief_id"].nullable is False
    assert columns["parent_version_id"].nullable is True
    assert columns["status"].nullable is False
    assert columns["version"].nullable is False
    assert columns["schema_version"].nullable is False
    assert columns["is_outdated"].nullable is False

    brief_fk = next(iter(columns["marketing_brief_id"].foreign_keys))
    parent_fk = next(iter(columns["parent_version_id"].foreign_keys))

    assert brief_fk.target_fullname == "marketing_briefs.id"
    assert brief_fk.ondelete == "CASCADE"

    assert parent_fk.target_fullname == "research_plans.id"
    assert parent_fk.ondelete == "SET NULL"


def test_research_plan_unique_version_per_marketing_brief():
    unique_constraints = [
        constraint
        for constraint in ResearchPlan.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    ]

    matching_constraint = next(
        constraint
        for constraint in unique_constraints
        if constraint.name == "uq_research_plans_marketing_brief_version"
    )

    assert [column.name for column in matching_constraint.columns] == [
        "marketing_brief_id",
        "version",
    ]