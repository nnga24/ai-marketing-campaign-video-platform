from sqlalchemy import UniqueConstraint

from modules.common.enums import SourceType
from modules.strategy_engine.models import (
    Strategy,
    StrategyDecision,
    StrategyDecisionFinding,
    StrategyDecisionRequirement,
)


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

def test_strategy_decision_table_contract():
    columns = StrategyDecision.__table__.columns

    assert set(columns.keys()) == {
        "id",
        "strategy_id",
        "decision_kind",
        "statement",
        "rationale",
        "created_at",
        "updated_at",
        "source_type",
    }

    assert columns["strategy_id"].nullable is False
    assert columns["decision_kind"].nullable is False
    assert columns["statement"].nullable is False
    assert columns["rationale"].nullable is True
    assert columns["source_type"].nullable is False

    strategy_fk = next(iter(columns["strategy_id"].foreign_keys))

    assert strategy_fk.target_fullname == "strategies.id"
    assert strategy_fk.ondelete == "CASCADE"

    assert "status" not in columns
    assert "version" not in columns
    assert "schema_version" not in columns
    assert "is_outdated" not in columns


def test_strategy_decision_requires_explicit_source_type():
    column = StrategyDecision.__table__.columns["source_type"]

    assert column.type.enum_class is SourceType
    assert column.default is None
    assert column.server_default is None

def test_strategy_decision_finding_table_contract():
    columns = StrategyDecisionFinding.__table__.columns

    assert set(columns.keys()) == {
        "id",
        "strategy_decision_id",
        "research_finding_id",
        "created_at",
        "updated_at",
    }

    assert columns["strategy_decision_id"].nullable is False
    assert columns["research_finding_id"].nullable is False

    decision_fk = next(
        iter(columns["strategy_decision_id"].foreign_keys)
    )
    finding_fk = next(
        iter(columns["research_finding_id"].foreign_keys)
    )

    assert decision_fk.target_fullname == "strategy_decisions.id"
    assert decision_fk.ondelete == "CASCADE"

    assert finding_fk.target_fullname == "research_findings.id"
    assert finding_fk.ondelete == "RESTRICT"

    assert "source_type" not in columns
    assert "status" not in columns
    assert "version" not in columns
    assert "schema_version" not in columns
    assert "is_outdated" not in columns


def test_strategy_decision_finding_unique_pair():
    unique_constraints = [
        constraint
        for constraint in StrategyDecisionFinding.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    ]

    matching_constraint = next(
        constraint
        for constraint in unique_constraints
        if constraint.name == "uq_strategy_decision_finding_pair"
    )

    assert [column.name for column in matching_constraint.columns] == [
        "strategy_decision_id",
        "research_finding_id",
    ]

def test_strategy_decision_requirement_table_contract():
    columns = StrategyDecisionRequirement.__table__.columns

    assert set(columns.keys()) == {
        "id",
        "strategy_decision_id",
        "marketing_requirement_id",
        "created_at",
        "updated_at",
    }

    assert columns["strategy_decision_id"].nullable is False
    assert columns["marketing_requirement_id"].nullable is False

    decision_fk = next(
        iter(columns["strategy_decision_id"].foreign_keys)
    )
    requirement_fk = next(
        iter(columns["marketing_requirement_id"].foreign_keys)
    )

    assert decision_fk.target_fullname == "strategy_decisions.id"
    assert decision_fk.ondelete == "CASCADE"

    assert requirement_fk.target_fullname == "marketing_requirements.id"
    assert requirement_fk.ondelete == "RESTRICT"

    assert "source_type" not in columns
    assert "status" not in columns
    assert "version" not in columns
    assert "schema_version" not in columns
    assert "is_outdated" not in columns


def test_strategy_decision_requirement_unique_pair():
    unique_constraints = [
        constraint
        for constraint in StrategyDecisionRequirement.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    ]

    matching_constraint = next(
        constraint
        for constraint in unique_constraints
        if constraint.name == "uq_strategy_decision_requirement_pair"
    )

    assert [column.name for column in matching_constraint.columns] == [
        "strategy_decision_id",
        "marketing_requirement_id",
    ]