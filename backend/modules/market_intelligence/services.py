import uuid

from modules.market_intelligence.models import (
    ResearchPlan,
    ResearchRun,
    ResearchTask,
    ResearchTaskExecution,
)

class MarketIntelligenceInvariantError(ValueError):
    pass

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