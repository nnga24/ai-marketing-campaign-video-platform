import uuid

from modules.marketing_requirement.models import MarketingBrief


class MarketingRequirementInvariantError(ValueError):
    pass


def ensure_marketing_brief_parent_matches_project(
    *,
    project_id: uuid.UUID,
    parent: MarketingBrief | None,
) -> None:
    if parent is not None and parent.project_id != project_id:
        raise MarketingRequirementInvariantError(
            "MarketingBrief parent must belong to the same project."
        )


def build_marketing_brief_version(
    *,
    project_id: uuid.UUID,
    parent: MarketingBrief | None = None,
) -> MarketingBrief:
    ensure_marketing_brief_parent_matches_project(
        project_id=project_id,
        parent=parent,
    )

    return MarketingBrief(
        project_id=project_id,
        parent_version_id=parent.id if parent is not None else None,
        version=parent.version + 1 if parent is not None else 1,
    )