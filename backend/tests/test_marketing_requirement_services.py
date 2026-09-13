import uuid

import pytest

from modules.marketing_requirement.models import MarketingBrief
from modules.marketing_requirement.services import (
    MarketingRequirementInvariantError,
    build_marketing_brief_version,
    ensure_marketing_brief_parent_matches_project,
)


def test_marketing_brief_parent_invariant_accepts_same_project():
    project_id = uuid.uuid4()

    parent = MarketingBrief(
        id=uuid.uuid4(),
        project_id=project_id,
        version=1,
    )

    ensure_marketing_brief_parent_matches_project(
        project_id=project_id,
        parent=parent,
    )


def test_marketing_brief_parent_invariant_rejects_different_project():
    parent = MarketingBrief(
        id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        version=1,
    )

    with pytest.raises(
        MarketingRequirementInvariantError,
        match="MarketingBrief parent must belong to the same project.",
    ):
        ensure_marketing_brief_parent_matches_project(
            project_id=uuid.uuid4(),
            parent=parent,
        )


def test_build_first_marketing_brief_version():
    project_id = uuid.uuid4()

    brief = build_marketing_brief_version(
        project_id=project_id,
    )

    assert brief.project_id == project_id
    assert brief.parent_version_id is None
    assert brief.version == 1


def test_build_next_marketing_brief_version():
    project_id = uuid.uuid4()
    parent_id = uuid.uuid4()

    parent = MarketingBrief(
        id=parent_id,
        project_id=project_id,
        version=3,
    )

    brief = build_marketing_brief_version(
        project_id=project_id,
        parent=parent,
    )

    assert brief.project_id == project_id
    assert brief.parent_version_id == parent_id
    assert brief.version == 4


def test_build_marketing_brief_version_rejects_cross_project_parent():
    parent = MarketingBrief(
        id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        version=2,
    )

    with pytest.raises(MarketingRequirementInvariantError):
        build_marketing_brief_version(
            project_id=uuid.uuid4(),
            parent=parent,
        )