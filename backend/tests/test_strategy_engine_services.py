import uuid

import pytest

from modules.marketing_requirement.models import (
    MarketingBrief,
    MarketingRequirement,
)
from modules.market_intelligence.models import (
    ResearchFinding,
    ResearchPlan,
    ResearchRun,
)
from modules.market_intelligence.enums import ResearchRunStatus
from modules.strategy_engine.models import Strategy, StrategyDecision
from modules.strategy_engine.services import (
    StrategyEngineInvariantError,
    build_strategy_version,
    ensure_strategy_parent_matches_project,
    ensure_strategy_research_run_matches_project,
    build_strategy_decision_finding_link,
    ensure_strategy_decision_finding_matches_strategy_run,
    ensure_research_run_ready_for_strategy,
    build_strategy_decision_requirement_link,
    ensure_strategy_decision_requirement_matches_strategy_brief,
)


def build_matching_research_lineage(project_id: uuid.UUID):
    marketing_brief = MarketingBrief(
        id=uuid.uuid4(),
        project_id=project_id,
        version=1,
    )
    research_plan = ResearchPlan(
        id=uuid.uuid4(),
        marketing_brief_id=marketing_brief.id,
        version=1,
    )
    research_run = ResearchRun(
        id=uuid.uuid4(),
        research_plan_id=research_plan.id,
        status=ResearchRunStatus.SUCCEEDED,
    )
    return marketing_brief, research_plan, research_run


def test_strategy_research_lineage_accepts_matching_project():
    project_id = uuid.uuid4()
    marketing_brief, research_plan, research_run = (
        build_matching_research_lineage(project_id)
    )

    ensure_strategy_research_run_matches_project(
        project_id=project_id,
        research_run=research_run,
        research_plan=research_plan,
        marketing_brief=marketing_brief,
    )


def test_strategy_research_lineage_rejects_run_plan_mismatch():
    project_id = uuid.uuid4()
    marketing_brief, research_plan, research_run = (
        build_matching_research_lineage(project_id)
    )
    research_run.research_plan_id = uuid.uuid4()

    with pytest.raises(
        StrategyEngineInvariantError,
        match="ResearchRun must belong to the supplied ResearchPlan.",
    ):
        ensure_strategy_research_run_matches_project(
            project_id=project_id,
            research_run=research_run,
            research_plan=research_plan,
            marketing_brief=marketing_brief,
        )


def test_strategy_research_lineage_rejects_plan_brief_mismatch():
    project_id = uuid.uuid4()
    marketing_brief, research_plan, research_run = (
        build_matching_research_lineage(project_id)
    )
    research_plan.marketing_brief_id = uuid.uuid4()

    with pytest.raises(
        StrategyEngineInvariantError,
        match="ResearchPlan must belong to the supplied MarketingBrief.",
    ):
        ensure_strategy_research_run_matches_project(
            project_id=project_id,
            research_run=research_run,
            research_plan=research_plan,
            marketing_brief=marketing_brief,
        )


def test_strategy_research_lineage_rejects_cross_project():
    project_id = uuid.uuid4()
    marketing_brief, research_plan, research_run = (
        build_matching_research_lineage(uuid.uuid4())
    )

    with pytest.raises(
        StrategyEngineInvariantError,
        match="ResearchRun lineage must belong to the Strategy project.",
    ):
        ensure_strategy_research_run_matches_project(
            project_id=project_id,
            research_run=research_run,
            research_plan=research_plan,
            marketing_brief=marketing_brief,
        )


def test_strategy_parent_rejects_cross_project():
    parent = Strategy(
        id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        research_run_id=uuid.uuid4(),
        version=1,
    )

    with pytest.raises(
        StrategyEngineInvariantError,
        match="Strategy parent must belong to the same project.",
    ):
        ensure_strategy_parent_matches_project(
            project_id=uuid.uuid4(),
            parent=parent,
        )


def test_build_first_strategy_version():
    project_id = uuid.uuid4()
    marketing_brief, research_plan, research_run = (
        build_matching_research_lineage(project_id)
    )

    strategy = build_strategy_version(
        project_id=project_id,
        research_run=research_run,
        research_plan=research_plan,
        marketing_brief=marketing_brief,
    )

    assert strategy.project_id == project_id
    assert strategy.research_run_id == research_run.id
    assert strategy.parent_version_id is None
    assert strategy.version == 1


def test_build_next_strategy_version_allows_new_research_run():
    project_id = uuid.uuid4()

    parent = Strategy(
        id=uuid.uuid4(),
        project_id=project_id,
        research_run_id=uuid.uuid4(),
        version=2,
    )

    marketing_brief, research_plan, research_run = (
        build_matching_research_lineage(project_id)
    )

    strategy = build_strategy_version(
        project_id=project_id,
        research_run=research_run,
        research_plan=research_plan,
        marketing_brief=marketing_brief,
        parent=parent,
    )

    assert strategy.project_id == project_id
    assert strategy.research_run_id == research_run.id
    assert strategy.parent_version_id == parent.id
    assert strategy.version == 3


def test_build_strategy_version_rejects_cross_project_parent():
    project_id = uuid.uuid4()
    marketing_brief, research_plan, research_run = (
        build_matching_research_lineage(project_id)
    )

    parent = Strategy(
        id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        research_run_id=uuid.uuid4(),
        version=1,
    )

    with pytest.raises(StrategyEngineInvariantError):
        build_strategy_version(
            project_id=project_id,
            research_run=research_run,
            research_plan=research_plan,
            marketing_brief=marketing_brief,
            parent=parent,
        )

def test_strategy_decision_finding_lineage_accepts_matching_strategy_run():
    strategy_id = uuid.uuid4()
    research_run_id = uuid.uuid4()

    strategy = Strategy(
        id=strategy_id,
        project_id=uuid.uuid4(),
        research_run_id=research_run_id,
        version=1,
    )
    decision = StrategyDecision(
        id=uuid.uuid4(),
        strategy_id=strategy_id,
    )
    finding = ResearchFinding(
        id=uuid.uuid4(),
        research_run_id=research_run_id,
    )

    ensure_strategy_decision_finding_matches_strategy_run(
        strategy_decision=decision,
        strategy=strategy,
        research_finding=finding,
    )


def test_strategy_decision_finding_lineage_rejects_wrong_strategy():
    strategy = Strategy(
        id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        research_run_id=uuid.uuid4(),
        version=1,
    )
    decision = StrategyDecision(
        id=uuid.uuid4(),
        strategy_id=uuid.uuid4(),
    )
    finding = ResearchFinding(
        id=uuid.uuid4(),
        research_run_id=strategy.research_run_id,
    )

    with pytest.raises(
        StrategyEngineInvariantError,
        match="StrategyDecision must belong to the supplied Strategy.",
    ):
        ensure_strategy_decision_finding_matches_strategy_run(
            strategy_decision=decision,
            strategy=strategy,
            research_finding=finding,
        )


def test_strategy_decision_finding_lineage_rejects_cross_run_finding():
    strategy_id = uuid.uuid4()

    strategy = Strategy(
        id=strategy_id,
        project_id=uuid.uuid4(),
        research_run_id=uuid.uuid4(),
        version=1,
    )
    decision = StrategyDecision(
        id=uuid.uuid4(),
        strategy_id=strategy_id,
    )
    finding = ResearchFinding(
        id=uuid.uuid4(),
        research_run_id=uuid.uuid4(),
    )

    with pytest.raises(
        StrategyEngineInvariantError,
        match=(
            "ResearchFinding must belong to the ResearchRun "
            "used by the Strategy."
        ),
    ):
        ensure_strategy_decision_finding_matches_strategy_run(
            strategy_decision=decision,
            strategy=strategy,
            research_finding=finding,
        )


def test_build_strategy_decision_finding_link():
    strategy_id = uuid.uuid4()
    research_run_id = uuid.uuid4()
    decision_id = uuid.uuid4()
    finding_id = uuid.uuid4()

    strategy = Strategy(
        id=strategy_id,
        project_id=uuid.uuid4(),
        research_run_id=research_run_id,
        version=1,
    )
    decision = StrategyDecision(
        id=decision_id,
        strategy_id=strategy_id,
    )
    finding = ResearchFinding(
        id=finding_id,
        research_run_id=research_run_id,
    )

    link = build_strategy_decision_finding_link(
        strategy_decision=decision,
        strategy=strategy,
        research_finding=finding,
    )

    assert link.strategy_decision_id == decision_id
    assert link.research_finding_id == finding_id


def test_build_strategy_decision_finding_link_rejects_cross_run():
    strategy_id = uuid.uuid4()

    strategy = Strategy(
        id=strategy_id,
        project_id=uuid.uuid4(),
        research_run_id=uuid.uuid4(),
        version=1,
    )
    decision = StrategyDecision(
        id=uuid.uuid4(),
        strategy_id=strategy_id,
    )
    finding = ResearchFinding(
        id=uuid.uuid4(),
        research_run_id=uuid.uuid4(),
    )

    with pytest.raises(StrategyEngineInvariantError):
        build_strategy_decision_finding_link(
            strategy_decision=decision,
            strategy=strategy,
            research_finding=finding,
        )

def test_research_run_ready_for_strategy_accepts_completed_states():
    for status in (
        ResearchRunStatus.SUCCEEDED,
        ResearchRunStatus.PARTIAL,
    ):
        research_run = ResearchRun(
            id=uuid.uuid4(),
            research_plan_id=uuid.uuid4(),
            status=status,
        )

        ensure_research_run_ready_for_strategy(
            research_run=research_run,
        )


def test_research_run_ready_for_strategy_rejects_unready_states():
    for status in (
        ResearchRunStatus.PENDING,
        ResearchRunStatus.RUNNING,
        ResearchRunStatus.FAILED,
        ResearchRunStatus.CANCELLED,
    ):
        research_run = ResearchRun(
            id=uuid.uuid4(),
            research_plan_id=uuid.uuid4(),
            status=status,
        )

        with pytest.raises(
            StrategyEngineInvariantError,
            match=(
                "ResearchRun must be SUCCEEDED or PARTIAL "
                "before Strategy creation."
            ),
        ):
            ensure_research_run_ready_for_strategy(
                research_run=research_run,
            )


def test_build_strategy_version_rejects_unready_research_run():
    project_id = uuid.uuid4()
    marketing_brief, research_plan, research_run = (
        build_matching_research_lineage(project_id)
    )
    research_run.status = ResearchRunStatus.RUNNING

    with pytest.raises(StrategyEngineInvariantError):
        build_strategy_version(
            project_id=project_id,
            research_run=research_run,
            research_plan=research_plan,
            marketing_brief=marketing_brief,
        )

def test_strategy_decision_requirement_lineage_accepts_matching_brief():
    project_id = uuid.uuid4()
    brief_id = uuid.uuid4()
    plan_id = uuid.uuid4()
    run_id = uuid.uuid4()
    strategy_id = uuid.uuid4()

    research_plan = ResearchPlan(
        id=plan_id,
        marketing_brief_id=brief_id,
        version=1,
    )
    research_run = ResearchRun(
        id=run_id,
        research_plan_id=plan_id,
        status=ResearchRunStatus.SUCCEEDED,
    )
    strategy = Strategy(
        id=strategy_id,
        project_id=project_id,
        research_run_id=run_id,
        version=1,
    )
    decision = StrategyDecision(
        id=uuid.uuid4(),
        strategy_id=strategy_id,
    )
    requirement = MarketingRequirement(
        id=uuid.uuid4(),
        marketing_brief_id=brief_id,
    )

    ensure_strategy_decision_requirement_matches_strategy_brief(
        strategy_decision=decision,
        strategy=strategy,
        marketing_requirement=requirement,
        research_run=research_run,
        research_plan=research_plan,
    )


def test_strategy_decision_requirement_lineage_rejects_wrong_strategy():
    brief_id = uuid.uuid4()
    plan_id = uuid.uuid4()
    run_id = uuid.uuid4()

    research_plan = ResearchPlan(
        id=plan_id,
        marketing_brief_id=brief_id,
        version=1,
    )
    research_run = ResearchRun(
        id=run_id,
        research_plan_id=plan_id,
    )
    strategy = Strategy(
        id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        research_run_id=run_id,
        version=1,
    )
    decision = StrategyDecision(
        id=uuid.uuid4(),
        strategy_id=uuid.uuid4(),
    )
    requirement = MarketingRequirement(
        id=uuid.uuid4(),
        marketing_brief_id=brief_id,
    )

    with pytest.raises(
        StrategyEngineInvariantError,
        match="StrategyDecision must belong to the supplied Strategy.",
    ):
        ensure_strategy_decision_requirement_matches_strategy_brief(
            strategy_decision=decision,
            strategy=strategy,
            marketing_requirement=requirement,
            research_run=research_run,
            research_plan=research_plan,
        )


def test_strategy_decision_requirement_lineage_rejects_wrong_run():
    brief_id = uuid.uuid4()
    plan_id = uuid.uuid4()

    research_plan = ResearchPlan(
        id=plan_id,
        marketing_brief_id=brief_id,
        version=1,
    )
    research_run = ResearchRun(
        id=uuid.uuid4(),
        research_plan_id=plan_id,
    )
    strategy_id = uuid.uuid4()
    strategy = Strategy(
        id=strategy_id,
        project_id=uuid.uuid4(),
        research_run_id=uuid.uuid4(),
        version=1,
    )
    decision = StrategyDecision(
        id=uuid.uuid4(),
        strategy_id=strategy_id,
    )
    requirement = MarketingRequirement(
        id=uuid.uuid4(),
        marketing_brief_id=brief_id,
    )

    with pytest.raises(
        StrategyEngineInvariantError,
        match="Strategy must use the supplied ResearchRun.",
    ):
        ensure_strategy_decision_requirement_matches_strategy_brief(
            strategy_decision=decision,
            strategy=strategy,
            marketing_requirement=requirement,
            research_run=research_run,
            research_plan=research_plan,
        )


def test_strategy_decision_requirement_lineage_rejects_wrong_plan():
    brief_id = uuid.uuid4()
    run_id = uuid.uuid4()

    research_plan = ResearchPlan(
        id=uuid.uuid4(),
        marketing_brief_id=brief_id,
        version=1,
    )
    research_run = ResearchRun(
        id=run_id,
        research_plan_id=uuid.uuid4(),
    )
    strategy_id = uuid.uuid4()
    strategy = Strategy(
        id=strategy_id,
        project_id=uuid.uuid4(),
        research_run_id=run_id,
        version=1,
    )
    decision = StrategyDecision(
        id=uuid.uuid4(),
        strategy_id=strategy_id,
    )
    requirement = MarketingRequirement(
        id=uuid.uuid4(),
        marketing_brief_id=brief_id,
    )

    with pytest.raises(
        StrategyEngineInvariantError,
        match="ResearchRun must belong to the supplied ResearchPlan.",
    ):
        ensure_strategy_decision_requirement_matches_strategy_brief(
            strategy_decision=decision,
            strategy=strategy,
            marketing_requirement=requirement,
            research_run=research_run,
            research_plan=research_plan,
        )


def test_strategy_decision_requirement_lineage_rejects_cross_brief_requirement():
    plan_id = uuid.uuid4()
    run_id = uuid.uuid4()
    strategy_id = uuid.uuid4()

    research_plan = ResearchPlan(
        id=plan_id,
        marketing_brief_id=uuid.uuid4(),
        version=1,
    )
    research_run = ResearchRun(
        id=run_id,
        research_plan_id=plan_id,
    )
    strategy = Strategy(
        id=strategy_id,
        project_id=uuid.uuid4(),
        research_run_id=run_id,
        version=1,
    )
    decision = StrategyDecision(
        id=uuid.uuid4(),
        strategy_id=strategy_id,
    )
    requirement = MarketingRequirement(
        id=uuid.uuid4(),
        marketing_brief_id=uuid.uuid4(),
    )

    with pytest.raises(
        StrategyEngineInvariantError,
        match=(
            "MarketingRequirement must belong to the MarketingBrief "
            "used by the Strategy research lineage."
        ),
    ):
        ensure_strategy_decision_requirement_matches_strategy_brief(
            strategy_decision=decision,
            strategy=strategy,
            marketing_requirement=requirement,
            research_run=research_run,
            research_plan=research_plan,
        )


def test_build_strategy_decision_requirement_link():
    brief_id = uuid.uuid4()
    plan_id = uuid.uuid4()
    run_id = uuid.uuid4()
    strategy_id = uuid.uuid4()
    decision_id = uuid.uuid4()
    requirement_id = uuid.uuid4()

    research_plan = ResearchPlan(
        id=plan_id,
        marketing_brief_id=brief_id,
        version=1,
    )
    research_run = ResearchRun(
        id=run_id,
        research_plan_id=plan_id,
    )
    strategy = Strategy(
        id=strategy_id,
        project_id=uuid.uuid4(),
        research_run_id=run_id,
        version=1,
    )
    decision = StrategyDecision(
        id=decision_id,
        strategy_id=strategy_id,
    )
    requirement = MarketingRequirement(
        id=requirement_id,
        marketing_brief_id=brief_id,
    )

    link = build_strategy_decision_requirement_link(
        strategy_decision=decision,
        strategy=strategy,
        marketing_requirement=requirement,
        research_run=research_run,
        research_plan=research_plan,
    )

    assert link.strategy_decision_id == decision_id
    assert link.marketing_requirement_id == requirement_id


def test_build_strategy_decision_requirement_link_rejects_cross_brief():
    plan_id = uuid.uuid4()
    run_id = uuid.uuid4()
    strategy_id = uuid.uuid4()

    research_plan = ResearchPlan(
        id=plan_id,
        marketing_brief_id=uuid.uuid4(),
        version=1,
    )
    research_run = ResearchRun(
        id=run_id,
        research_plan_id=plan_id,
    )
    strategy = Strategy(
        id=strategy_id,
        project_id=uuid.uuid4(),
        research_run_id=run_id,
        version=1,
    )
    decision = StrategyDecision(
        id=uuid.uuid4(),
        strategy_id=strategy_id,
    )
    requirement = MarketingRequirement(
        id=uuid.uuid4(),
        marketing_brief_id=uuid.uuid4(),
    )

    with pytest.raises(StrategyEngineInvariantError):
        build_strategy_decision_requirement_link(
            strategy_decision=decision,
            strategy=strategy,
            marketing_requirement=requirement,
            research_run=research_run,
            research_plan=research_plan,
        )