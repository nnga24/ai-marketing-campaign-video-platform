import uuid

from modules.market_intelligence.models import (
    ResearchEvidence,
    ResearchFinding,
    ResearchFindingEvidence,
    ResearchPlan,
    ResearchRun,
    ResearchTask,
    ResearchTaskExecution,
)

from datetime import datetime
from modules.market_intelligence.enums import (
    ResearchRunStatus,
    ResearchTaskExecutionStatus,
)
class MarketIntelligenceInvariantError(ValueError):
    pass

def ensure_research_evidence_matches_finding_run(
    *,
    research_finding: ResearchFinding,
    research_evidence: ResearchEvidence,
    task_execution: ResearchTaskExecution,
) -> None:
    if research_evidence.research_task_execution_id != task_execution.id:
        raise MarketIntelligenceInvariantError(
            "ResearchEvidence must belong to the supplied ResearchTaskExecution."
        )

    if task_execution.research_run_id != research_finding.research_run_id:
        raise MarketIntelligenceInvariantError(
            "ResearchEvidence must belong to the same ResearchRun as the ResearchFinding."
        )


def build_research_finding_evidence_link(
    *,
    research_finding: ResearchFinding,
    research_evidence: ResearchEvidence,
    task_execution: ResearchTaskExecution,
) -> ResearchFindingEvidence:
    ensure_research_evidence_matches_finding_run(
        research_finding=research_finding,
        research_evidence=research_evidence,
        task_execution=task_execution,
    )

    return ResearchFindingEvidence(
        research_finding_id=research_finding.id,
        research_evidence_id=research_evidence.id,
    )

_ALLOWED_RESEARCH_RUN_TRANSITIONS: dict[
    ResearchRunStatus,
    frozenset[ResearchRunStatus],
] = {
    ResearchRunStatus.PENDING: frozenset({
        ResearchRunStatus.RUNNING,
        ResearchRunStatus.CANCELLED,
    }),
    ResearchRunStatus.RUNNING: frozenset({
        ResearchRunStatus.SUCCEEDED,
        ResearchRunStatus.PARTIAL,
        ResearchRunStatus.FAILED,
        ResearchRunStatus.CANCELLED,
    }),
    ResearchRunStatus.SUCCEEDED: frozenset(),
    ResearchRunStatus.PARTIAL: frozenset(),
    ResearchRunStatus.FAILED: frozenset(),
    ResearchRunStatus.CANCELLED: frozenset(),
}

_ALLOWED_RESEARCH_TASK_EXECUTION_TRANSITIONS: dict[
    ResearchTaskExecutionStatus,
    frozenset[ResearchTaskExecutionStatus],
] = {
    ResearchTaskExecutionStatus.PENDING: frozenset({
        ResearchTaskExecutionStatus.RUNNING,
        ResearchTaskExecutionStatus.CANCELLED,
    }),
    ResearchTaskExecutionStatus.RUNNING: frozenset({
        ResearchTaskExecutionStatus.SUCCEEDED,
        ResearchTaskExecutionStatus.FAILED,
        ResearchTaskExecutionStatus.CANCELLED,
    }),
    ResearchTaskExecutionStatus.SUCCEEDED: frozenset(),
    ResearchTaskExecutionStatus.FAILED: frozenset(),
    ResearchTaskExecutionStatus.CANCELLED: frozenset(),
}


def ensure_research_task_execution_transition_allowed(
    *,
    execution: ResearchTaskExecution,
    target_status: ResearchTaskExecutionStatus,
) -> None:
    current_status = execution.status

    if (
        target_status
        not in _ALLOWED_RESEARCH_TASK_EXECUTION_TRANSITIONS[current_status]
    ):
        raise MarketIntelligenceInvariantError(
            "ResearchTaskExecution transition "
            f"{current_status.value} -> {target_status.value} "
            "is not allowed."
        )

def ensure_research_run_transition_allowed(
    *,
    research_run: ResearchRun,
    target_status: ResearchRunStatus,
) -> None:
    current_status = research_run.status

    if target_status not in _ALLOWED_RESEARCH_RUN_TRANSITIONS[current_status]:
        raise MarketIntelligenceInvariantError(
            "ResearchRun transition "
            f"{current_status.value} -> {target_status.value} "
            "is not allowed."
        )

def transition_research_task_execution(
    *,
    execution: ResearchTaskExecution,
    target_status: ResearchTaskExecutionStatus,
    transitioned_at: datetime,
) -> ResearchTaskExecution:
    ensure_research_task_execution_transition_allowed(
        execution=execution,
        target_status=target_status,
    )

    if target_status is ResearchTaskExecutionStatus.RUNNING:
        execution.status = target_status
        execution.started_at = transitioned_at
        return execution

    if (
        execution.started_at is not None
        and transitioned_at < execution.started_at
    ):
        raise MarketIntelligenceInvariantError(
            "ResearchTaskExecution finished_at cannot be earlier than started_at."
        )

    execution.status = target_status
    execution.finished_at = transitioned_at

    return execution


def transition_research_run(
    *,
    research_run: ResearchRun,
    target_status: ResearchRunStatus,
    transitioned_at: datetime,
) -> ResearchRun:
    ensure_research_run_transition_allowed(
        research_run=research_run,
        target_status=target_status,
    )

    if target_status is ResearchRunStatus.RUNNING:
        research_run.status = target_status
        research_run.started_at = transitioned_at
        return research_run

    if (
        research_run.started_at is not None
        and transitioned_at < research_run.started_at
    ):
        raise MarketIntelligenceInvariantError(
            "ResearchRun finished_at cannot be earlier than started_at."
        )

    research_run.status = target_status
    research_run.finished_at = transitioned_at

    return research_run

def ensure_research_task_matches_run_plan(
    *,
    research_run: ResearchRun,
    research_task: ResearchTask,
) -> None:
    if research_task.research_plan_id != research_run.research_plan_id:
        raise MarketIntelligenceInvariantError(
            "ResearchTask must belong to the ResearchPlan executed by the ResearchRun."
        )

def build_research_task_execution(
    *,
    research_run: ResearchRun,
    research_task: ResearchTask,
) -> ResearchTaskExecution:
    ensure_research_task_matches_run_plan(
        research_run=research_run,
        research_task=research_task,
    )

    return ResearchTaskExecution(
        research_run_id=research_run.id,
        research_task_id=research_task.id,
    )

def ensure_research_plan_parent_matches_marketing_brief(
    *,
    marketing_brief_id: uuid.UUID,
    parent: ResearchPlan | None,
) -> None:
    if (
        parent is not None
        and parent.marketing_brief_id != marketing_brief_id
    ):
        raise MarketIntelligenceInvariantError(
            "ResearchPlan parent must belong to the same marketing brief."
        )


def build_research_plan_version(
    *,
    marketing_brief_id: uuid.UUID,
    parent: ResearchPlan | None = None,
) -> ResearchPlan:
    ensure_research_plan_parent_matches_marketing_brief(
        marketing_brief_id=marketing_brief_id,
        parent=parent,
    )

    return ResearchPlan(
        marketing_brief_id=marketing_brief_id,
        parent_version_id=parent.id if parent is not None else None,
        version=parent.version + 1 if parent is not None else 1,
    )