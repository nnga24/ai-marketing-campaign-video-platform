import uuid

import pytest

from modules.market_intelligence.models import (
    ResearchPlan,
    ResearchRun,
    ResearchTask,
)
from modules.market_intelligence.services import (
    MarketIntelligenceInvariantError,
    build_research_plan_version,
    build_research_task_execution,
    ensure_research_plan_parent_matches_marketing_brief,
    ensure_research_task_matches_run_plan,
)


def test_research_plan_parent_invariant_accepts_same_marketing_brief():
    marketing_brief_id = uuid.uuid4()

    parent = ResearchPlan(
        id=uuid.uuid4(),
        marketing_brief_id=marketing_brief_id,
        version=1,
    )

    ensure_research_plan_parent_matches_marketing_brief(
        marketing_brief_id=marketing_brief_id,
        parent=parent,
    )


def test_research_plan_parent_invariant_rejects_different_marketing_brief():
    parent = ResearchPlan(
        id=uuid.uuid4(),
        marketing_brief_id=uuid.uuid4(),
        version=1,
    )

    with pytest.raises(
        MarketIntelligenceInvariantError,
        match="ResearchPlan parent must belong to the same marketing brief.",
    ):
        ensure_research_plan_parent_matches_marketing_brief(
            marketing_brief_id=uuid.uuid4(),
            parent=parent,
        )


def test_build_first_research_plan_version():
    marketing_brief_id = uuid.uuid4()

    plan = build_research_plan_version(
        marketing_brief_id=marketing_brief_id,
    )

    assert plan.marketing_brief_id == marketing_brief_id
    assert plan.parent_version_id is None
    assert plan.version == 1


def test_build_next_research_plan_version():
    marketing_brief_id = uuid.uuid4()
    parent_id = uuid.uuid4()

    parent = ResearchPlan(
        id=parent_id,
        marketing_brief_id=marketing_brief_id,
        version=2,
    )

    plan = build_research_plan_version(
        marketing_brief_id=marketing_brief_id,
        parent=parent,
    )

    assert plan.marketing_brief_id == marketing_brief_id
    assert plan.parent_version_id == parent_id
    assert plan.version == 3


def test_build_research_plan_version_rejects_cross_brief_parent():
    parent = ResearchPlan(
        id=uuid.uuid4(),
        marketing_brief_id=uuid.uuid4(),
        version=4,
    )

    with pytest.raises(MarketIntelligenceInvariantError):
        build_research_plan_version(
            marketing_brief_id=uuid.uuid4(),
            parent=parent,
        )

def test_research_task_run_plan_invariant_accepts_matching_plan():
    research_plan_id = uuid.uuid4()

    research_run = ResearchRun(
        id=uuid.uuid4(),
        research_plan_id=research_plan_id,
    )
    research_task = ResearchTask(
        id=uuid.uuid4(),
        research_plan_id=research_plan_id,
    )

    ensure_research_task_matches_run_plan(
        research_run=research_run,
        research_task=research_task,
    )


def test_research_task_run_plan_invariant_rejects_different_plan():
    research_run = ResearchRun(
        id=uuid.uuid4(),
        research_plan_id=uuid.uuid4(),
    )
    research_task = ResearchTask(
        id=uuid.uuid4(),
        research_plan_id=uuid.uuid4(),
    )

    with pytest.raises(
        MarketIntelligenceInvariantError,
        match=(
            "ResearchTask must belong to the ResearchPlan "
            "executed by the ResearchRun."
        ),
    ):
        ensure_research_task_matches_run_plan(
            research_run=research_run,
            research_task=research_task,
        )


def test_build_research_task_execution():
    research_plan_id = uuid.uuid4()
    research_run_id = uuid.uuid4()
    research_task_id = uuid.uuid4()

    research_run = ResearchRun(
        id=research_run_id,
        research_plan_id=research_plan_id,
    )
    research_task = ResearchTask(
        id=research_task_id,
        research_plan_id=research_plan_id,
    )

    execution = build_research_task_execution(
        research_run=research_run,
        research_task=research_task,
    )

    assert execution.research_run_id == research_run_id
    assert execution.research_task_id == research_task_id


def test_build_research_task_execution_rejects_cross_plan_task():
    research_run = ResearchRun(
        id=uuid.uuid4(),
        research_plan_id=uuid.uuid4(),
    )
    research_task = ResearchTask(
        id=uuid.uuid4(),
        research_plan_id=uuid.uuid4(),
    )

    with pytest.raises(MarketIntelligenceInvariantError):
        build_research_task_execution(
            research_run=research_run,
            research_task=research_task,
        )