from sqlalchemy import UniqueConstraint

from modules.strategy_engine.models import Strategy


def test_strategy_table_contract():
    columns = Strategy.__table__.columns

    assert set(columns.keys()) == {
        "id",
        "project_id",
        "research_run_id",
        "parent_version_id",
        "created_at",
        "updated_at",
        "status",
        "version",
        "schema_version",
        "is_outdated",
    }

    assert columns["project_id"].nullable is False
    assert columns["research_run_id"].nullable is False
    assert columns["parent_version_id"].nullable is True

    project_fk = next(iter(columns["project_id"].foreign_keys))
    research_run_fk = next(iter(columns["research_run_id"].foreign_keys))
    parent_fk = next(iter(columns["parent_version_id"].foreign_keys))

    assert project_fk.target_fullname == "projects.id"
    assert project_fk.ondelete == "CASCADE"

    assert research_run_fk.target_fullname == "research_runs.id"
    assert research_run_fk.ondelete == "RESTRICT"

    assert parent_fk.target_fullname == "strategies.id"
    assert parent_fk.ondelete == "SET NULL"

    assert "source_type" not in columns


def test_strategy_unique_version_per_project():
    unique_constraints = [
        constraint
        for constraint in Strategy.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    ]

    matching_constraint = next(
        constraint
        for constraint in unique_constraints
        if constraint.name == "uq_strategies_project_version"
    )

    assert [column.name for column in matching_constraint.columns] == [
        "project_id",
        "version",
    ]