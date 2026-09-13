import uuid

import pytest

from modules.market_intelligence.models import ResearchPlan
from modules.market_intelligence.services import (
    MarketIntelligenceInvariantError,
    build_research_plan_version,
    ensure_research_plan_parent_matches_marketing_brief,
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