from sqlalchemy import UniqueConstraint

from modules.campaign_planning.models import Campaign, CampaignPlan


def test_campaign_table_contract():
    columns = Campaign.__table__.columns

    assert set(columns.keys()) == {
        "id",
        "project_id",
        "name",
        "slug",
        "created_at",
        "updated_at",
        "status",
    }

    assert columns["project_id"].nullable is False
    assert columns["name"].nullable is False
    assert columns["slug"].nullable is False
    assert columns["status"].nullable is False

    project_fk = next(iter(columns["project_id"].foreign_keys))

    assert project_fk.target_fullname == "projects.id"
    assert project_fk.ondelete == "CASCADE"

    assert "source_type" not in columns
    assert "version" not in columns
    assert "schema_version" not in columns
    assert "is_outdated" not in columns


def test_campaign_project_slug_unique_constraint():
    unique_constraints = [
        constraint
        for constraint in Campaign.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    ]

    matching_constraint = next(
        constraint
        for constraint in unique_constraints
        if constraint.name == "uq_campaigns_project_slug"
    )

    assert [column.name for column in matching_constraint.columns] == [
        "project_id",
        "slug",
    ]

def test_campaign_plan_table_contract():
    columns = CampaignPlan.__table__.columns

    assert set(columns.keys()) == {
        "id",
        "campaign_id",
        "strategy_id",
        "parent_version_id",
        "created_at",
        "updated_at",
        "status",
        "version",
        "schema_version",
        "is_outdated",
    }

    assert columns["campaign_id"].nullable is False
    assert columns["strategy_id"].nullable is False
    assert columns["parent_version_id"].nullable is True

    campaign_fk = next(iter(columns["campaign_id"].foreign_keys))
    strategy_fk = next(iter(columns["strategy_id"].foreign_keys))
    parent_fk = next(iter(columns["parent_version_id"].foreign_keys))

    assert campaign_fk.target_fullname == "campaigns.id"
    assert campaign_fk.ondelete == "CASCADE"

    assert strategy_fk.target_fullname == "strategies.id"
    assert strategy_fk.ondelete == "RESTRICT"

    assert parent_fk.target_fullname == "campaign_plans.id"
    assert parent_fk.ondelete == "SET NULL"

    assert "source_type" not in columns


def test_campaign_plan_campaign_version_unique_constraint():
    unique_constraints = [
        constraint
        for constraint in CampaignPlan.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    ]

    matching_constraint = next(
        constraint
        for constraint in unique_constraints
        if constraint.name == "uq_campaign_plans_campaign_version"
    )

    assert [column.name for column in matching_constraint.columns] == [
        "campaign_id",
        "version",
    ]