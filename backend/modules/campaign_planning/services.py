from modules.campaign_planning.models import Campaign, CampaignPlan
from modules.strategy_engine.models import Strategy


class CampaignPlanningInvariantError(ValueError):
    pass


def ensure_campaign_strategy_matches_project(
    *,
    campaign: Campaign,
    strategy: Strategy,
) -> None:
    if campaign.project_id != strategy.project_id:
        raise CampaignPlanningInvariantError(
            "Strategy must belong to the same project as the Campaign."
        )

def ensure_campaign_plan_parent_matches_campaign(
    *,
    campaign: Campaign,
    parent: CampaignPlan | None,
) -> None:
    if parent is not None and parent.campaign_id != campaign.id:
        raise CampaignPlanningInvariantError(
            "CampaignPlan parent must belong to the same Campaign."
        )

def build_campaign_plan_version(
    *,
    campaign: Campaign,
    strategy: Strategy,
    parent: CampaignPlan | None = None,
) -> CampaignPlan:
    ensure_campaign_strategy_matches_project(
        campaign=campaign,
        strategy=strategy,
    )

    ensure_campaign_plan_parent_matches_campaign(
        campaign=campaign,
        parent=parent,
    )

    return CampaignPlan(
        campaign_id=campaign.id,
        strategy_id=strategy.id,
        parent_version_id=parent.id if parent is not None else None,
        version=parent.version + 1 if parent is not None else 1,
    )