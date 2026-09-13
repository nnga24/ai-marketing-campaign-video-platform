import uuid

import pytest

from modules.campaign_planning.models import Campaign, CampaignPlan
from modules.campaign_planning.services import (
    CampaignPlanningInvariantError,
    build_campaign_plan_version,
    ensure_campaign_plan_parent_matches_campaign,
    ensure_campaign_strategy_matches_project,
)
from modules.strategy_engine.models import Strategy


def build_campaign(*, project_id: uuid.UUID) -> Campaign:
    return Campaign(
        id=uuid.uuid4(),
        project_id=project_id,
        name="Test Campaign",
        slug=f"campaign-{uuid.uuid4()}",
    )


def build_strategy(*, project_id: uuid.UUID) -> Strategy:
    return Strategy(
        id=uuid.uuid4(),
        project_id=project_id,
        research_run_id=uuid.uuid4(),
        version=1,
    )


def test_campaign_strategy_invariant_accepts_same_project():
    project_id = uuid.uuid4()

    campaign = build_campaign(project_id=project_id)
    strategy = build_strategy(project_id=project_id)

    ensure_campaign_strategy_matches_project(
        campaign=campaign,
        strategy=strategy,
    )


def test_campaign_strategy_invariant_rejects_cross_project():
    campaign = build_campaign(project_id=uuid.uuid4())
    strategy = build_strategy(project_id=uuid.uuid4())

    with pytest.raises(
        CampaignPlanningInvariantError,
        match="Strategy must belong to the same project as the Campaign.",
    ):
        ensure_campaign_strategy_matches_project(
            campaign=campaign,
            strategy=strategy,
        )


def test_campaign_plan_parent_invariant_accepts_same_campaign():
    project_id = uuid.uuid4()
    campaign = build_campaign(project_id=project_id)

    parent = CampaignPlan(
        id=uuid.uuid4(),
        campaign_id=campaign.id,
        strategy_id=uuid.uuid4(),
        version=1,
    )

    ensure_campaign_plan_parent_matches_campaign(
        campaign=campaign,
        parent=parent,
    )


def test_campaign_plan_parent_invariant_rejects_cross_campaign():
    project_id = uuid.uuid4()
    campaign = build_campaign(project_id=project_id)

    parent = CampaignPlan(
        id=uuid.uuid4(),
        campaign_id=uuid.uuid4(),
        strategy_id=uuid.uuid4(),
        version=1,
    )

    with pytest.raises(
        CampaignPlanningInvariantError,
        match="CampaignPlan parent must belong to the same Campaign.",
    ):
        ensure_campaign_plan_parent_matches_campaign(
            campaign=campaign,
            parent=parent,
        )


def test_build_campaign_plan_first_version():
    project_id = uuid.uuid4()
    campaign = build_campaign(project_id=project_id)
    strategy = build_strategy(project_id=project_id)

    plan = build_campaign_plan_version(
        campaign=campaign,
        strategy=strategy,
    )

    assert plan.campaign_id == campaign.id
    assert plan.strategy_id == strategy.id
    assert plan.parent_version_id is None
    assert plan.version == 1


def test_build_campaign_plan_next_version_can_use_new_strategy():
    project_id = uuid.uuid4()
    campaign = build_campaign(project_id=project_id)

    parent = CampaignPlan(
        id=uuid.uuid4(),
        campaign_id=campaign.id,
        strategy_id=uuid.uuid4(),
        version=1,
    )

    new_strategy = build_strategy(project_id=project_id)

    plan = build_campaign_plan_version(
        campaign=campaign,
        strategy=new_strategy,
        parent=parent,
    )

    assert plan.campaign_id == campaign.id
    assert plan.strategy_id == new_strategy.id
    assert plan.parent_version_id == parent.id
    assert plan.version == 2


def test_build_campaign_plan_rejects_cross_project_strategy():
    campaign = build_campaign(project_id=uuid.uuid4())
    strategy = build_strategy(project_id=uuid.uuid4())

    with pytest.raises(CampaignPlanningInvariantError):
        build_campaign_plan_version(
            campaign=campaign,
            strategy=strategy,
        )