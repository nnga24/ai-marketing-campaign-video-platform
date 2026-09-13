import uuid

from modules.marketing_requirement.models import MarketingBrief
from modules.market_intelligence.models import (
    ResearchFinding,
    ResearchPlan,
    ResearchRun,
)
from modules.strategy_engine.models import (
    Strategy,
    StrategyDecision,
    StrategyDecisionFinding,
)

class StrategyEngineInvariantError(ValueError):
    pass

def ensure_strategy_decision_finding_matches_strategy_run(
    *,
    strategy_decision: StrategyDecision,
    strategy: Strategy,
    research_finding: ResearchFinding,
) -> None:
    if strategy_decision.strategy_id != strategy.id:
        raise StrategyEngineInvariantError(
            "StrategyDecision must belong to the supplied Strategy."
        )

    if research_finding.research_run_id != strategy.research_run_id:
        raise StrategyEngineInvariantError(
            "ResearchFinding must belong to the ResearchRun used by the Strategy."
        )

def build_strategy_decision_finding_link(
    *,
    strategy_decision: StrategyDecision,
    strategy: Strategy,
    research_finding: ResearchFinding,
) -> StrategyDecisionFinding:
    ensure_strategy_decision_finding_matches_strategy_run(
        strategy_decision=strategy_decision,
        strategy=strategy,
        research_finding=research_finding,
    )

    return StrategyDecisionFinding(
        strategy_decision_id=strategy_decision.id,
        research_finding_id=research_finding.id,
    )
def ensure_strategy_research_run_matches_project(
    *,
    project_id: uuid.UUID,
    research_run: ResearchRun,
    research_plan: ResearchPlan,
    marketing_brief: MarketingBrief,
) -> None:
    if research_run.research_plan_id != research_plan.id:
        raise StrategyEngineInvariantError(
            "ResearchRun must belong to the supplied ResearchPlan."
        )

    if research_plan.marketing_brief_id != marketing_brief.id:
        raise StrategyEngineInvariantError(
            "ResearchPlan must belong to the supplied MarketingBrief."
        )

    if marketing_brief.project_id != project_id:
        raise StrategyEngineInvariantError(
            "ResearchRun lineage must belong to the Strategy project."
        )


def ensure_strategy_parent_matches_project(
    *,
    project_id: uuid.UUID,
    parent: Strategy | None,
) -> None:
    if parent is not None and parent.project_id != project_id:
        raise StrategyEngineInvariantError(
            "Strategy parent must belong to the same project."
        )


def build_strategy_version(
    *,
    project_id: uuid.UUID,
    research_run: ResearchRun,
    research_plan: ResearchPlan,
    marketing_brief: MarketingBrief,
    parent: Strategy | None = None,
) -> Strategy:
    ensure_strategy_research_run_matches_project(
        project_id=project_id,
        research_run=research_run,
        research_plan=research_plan,
        marketing_brief=marketing_brief,
    )

    ensure_strategy_parent_matches_project(
        project_id=project_id,
        parent=parent,
    )

    return Strategy(
        project_id=project_id,
        research_run_id=research_run.id,
        parent_version_id=parent.id if parent is not None else None,
        version=parent.version + 1 if parent is not None else 1,
    )
