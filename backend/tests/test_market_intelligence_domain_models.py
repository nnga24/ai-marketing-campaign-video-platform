from sqlalchemy import CheckConstraint, UniqueConstraint

from modules.common.enums import SourceType
from modules.market_intelligence.models import (
    ResearchEvidence,
    ResearchPlan,
    ResearchRun,
    ResearchTask,
    ResearchTaskExecution,
)
from modules.market_intelligence.enums import (
    ResearchRunStatus,
    ResearchTaskExecutionStatus,
)

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

def test_research_task_table_contract():
    columns = ResearchTask.__table__.columns

    assert set(columns.keys()) == {
        "id",
        "research_plan_id",
        "position",
        "objective",
        "created_at",
        "updated_at",
        "source_type",
    }

    assert columns["research_plan_id"].nullable is False
    assert columns["position"].nullable is False
    assert columns["objective"].nullable is False
    assert columns["source_type"].nullable is False

    plan_fk = next(iter(columns["research_plan_id"].foreign_keys))

    assert plan_fk.target_fullname == "research_plans.id"
    assert plan_fk.ondelete == "CASCADE"

    assert "status" not in columns
    assert "version" not in columns
    assert "schema_version" not in columns
    assert "is_outdated" not in columns


def test_research_task_unique_position_per_plan():
    unique_constraints = [
        constraint
        for constraint in ResearchTask.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    ]

    matching_constraint = next(
        constraint
        for constraint in unique_constraints
        if constraint.name == "uq_research_tasks_plan_position"
    )

    assert [column.name for column in matching_constraint.columns] == [
        "research_plan_id",
        "position",
    ]


def test_research_task_position_must_be_positive():
    check_constraints = [
        constraint
        for constraint in ResearchTask.__table__.constraints
        if isinstance(constraint, CheckConstraint)
    ]

    matching_constraint = next(
        constraint
        for constraint in check_constraints
        if constraint.name == "ck_research_tasks_position_positive"
    )

    assert str(matching_constraint.sqltext) == "position >= 1"


def test_research_task_requires_explicit_source_type():
    column = ResearchTask.__table__.columns["source_type"]

    assert column.type.enum_class is SourceType
    assert column.default is None
    assert column.server_default is None

def test_research_run_table_contract():
    columns = ResearchRun.__table__.columns

    assert set(columns.keys()) == {
        "id",
        "research_plan_id",
        "status",
        "started_at",
        "finished_at",
        "error_message",
        "created_at",
        "updated_at",
    }

    assert columns["research_plan_id"].nullable is False
    assert columns["status"].nullable is False

    assert columns["started_at"].nullable is True
    assert columns["finished_at"].nullable is True
    assert columns["error_message"].nullable is True

    plan_fk = next(iter(columns["research_plan_id"].foreign_keys))

    assert plan_fk.target_fullname == "research_plans.id"
    assert plan_fk.ondelete == "CASCADE"

    assert "source_type" not in columns
    assert "version" not in columns
    assert "schema_version" not in columns
    assert "is_outdated" not in columns


def test_research_run_status_contract():
    column = ResearchRun.__table__.columns["status"]

    assert column.type.enum_class is ResearchRunStatus
    assert [item.value for item in ResearchRunStatus] == [
        "PENDING",
        "RUNNING",
        "SUCCEEDED",
        "PARTIAL",
        "FAILED",
        "CANCELLED",
    ]


def test_research_run_defaults_to_pending():
    column = ResearchRun.__table__.columns["status"]

    assert column.default.arg is ResearchRunStatus.PENDING
    assert column.server_default.arg == ResearchRunStatus.PENDING.value

def test_research_task_execution_table_contract():
    columns = ResearchTaskExecution.__table__.columns

    assert set(columns.keys()) == {
        "id",
        "research_run_id",
        "research_task_id",
        "status",
        "started_at",
        "finished_at",
        "error_message",
        "created_at",
        "updated_at",
    }

    assert columns["research_run_id"].nullable is False
    assert columns["research_task_id"].nullable is False
    assert columns["status"].nullable is False

    assert columns["started_at"].nullable is True
    assert columns["finished_at"].nullable is True
    assert columns["error_message"].nullable is True

    run_fk = next(iter(columns["research_run_id"].foreign_keys))
    task_fk = next(iter(columns["research_task_id"].foreign_keys))

    assert run_fk.target_fullname == "research_runs.id"
    assert run_fk.ondelete == "CASCADE"

    assert task_fk.target_fullname == "research_tasks.id"
    assert task_fk.ondelete == "CASCADE"

    assert "source_type" not in columns
    assert "version" not in columns
    assert "schema_version" not in columns
    assert "is_outdated" not in columns


def test_research_task_execution_status_contract():
    column = ResearchTaskExecution.__table__.columns["status"]

    assert column.type.enum_class is ResearchTaskExecutionStatus
    assert [item.value for item in ResearchTaskExecutionStatus] == [
        "PENDING",
        "RUNNING",
        "SUCCEEDED",
        "FAILED",
        "CANCELLED",
    ]


def test_research_task_execution_defaults_to_pending():
    column = ResearchTaskExecution.__table__.columns["status"]

    assert column.default.arg is ResearchTaskExecutionStatus.PENDING
    assert (
        column.server_default.arg
        == ResearchTaskExecutionStatus.PENDING.value
    )


def test_research_task_execution_unique_per_run_and_task():
    unique_constraints = [
        constraint
        for constraint in ResearchTaskExecution.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    ]

    matching_constraint = next(
        constraint
        for constraint in unique_constraints
        if constraint.name == "uq_research_task_executions_run_task"
    )

    assert [column.name for column in matching_constraint.columns] == [
        "research_run_id",
        "research_task_id",
    ]

def test_research_evidence_table_contract():
    columns = ResearchEvidence.__table__.columns

    assert set(columns.keys()) == {
        "id",
        "research_task_execution_id",
        "source_kind",
        "provider_key",
        "source_name",
        "source_uri",
        "source_external_id",
        "title",
        "content_text",
        "content_fingerprint",
        "published_at",
        "retrieved_at",
        "created_at",
        "updated_at",
    }

    assert columns["research_task_execution_id"].nullable is False
    assert columns["source_kind"].nullable is False
    assert columns["content_text"].nullable is False
    assert columns["content_fingerprint"].nullable is False
    assert columns["retrieved_at"].nullable is False

    assert columns["provider_key"].nullable is True
    assert columns["source_name"].nullable is True
    assert columns["source_uri"].nullable is True
    assert columns["source_external_id"].nullable is True
    assert columns["title"].nullable is True
    assert columns["published_at"].nullable is True

    execution_fk = next(
        iter(columns["research_task_execution_id"].foreign_keys)
    )

    assert (
        execution_fk.target_fullname
        == "research_task_executions.id"
    )
    assert execution_fk.ondelete == "CASCADE"

    assert "source_type" not in columns
    assert "version" not in columns
    assert "schema_version" not in columns
    assert "is_outdated" not in columns


def test_research_evidence_string_lengths():
    columns = ResearchEvidence.__table__.columns

    assert columns["source_kind"].type.length == 64
    assert columns["provider_key"].type.length == 128
    assert columns["source_name"].type.length == 255
    assert columns["source_external_id"].type.length == 255
    assert columns["content_fingerprint"].type.length == 64


def test_research_evidence_unique_fingerprint_per_execution():
    unique_constraints = [
        constraint
        for constraint in ResearchEvidence.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    ]

    matching_constraint = next(
        constraint
        for constraint in unique_constraints
        if constraint.name
        == "uq_research_evidence_execution_fingerprint"
    )

    assert [column.name for column in matching_constraint.columns] == [
        "research_task_execution_id",
        "content_fingerprint",
    ]


def test_research_evidence_has_no_implicit_defaults():
    columns = ResearchEvidence.__table__.columns

    assert columns["source_kind"].default is None
    assert columns["content_text"].default is None
    assert columns["content_fingerprint"].default is None
    assert columns["retrieved_at"].default is None