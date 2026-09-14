from datetime import datetime, timezone
from uuid import uuid4

import pytest
from fastapi import HTTPException

from api.routes import projects_v2
from application.projects.dto import ProjectView
from application.projects.queries import ProjectNotFoundError
from modules.common.enums import EntityStatus
from api.schemas.projects import CreateProjectRequest
from application.projects.commands import (
    ProjectSlugConflictError,
    WorkspaceNotFoundError,
)

def test_read_project_maps_application_view_to_response(
    monkeypatch: pytest.MonkeyPatch,
):
    project_id = uuid4()
    workspace_id = uuid4()
    now = datetime.now(timezone.utc)

    project = ProjectView(
        id=project_id,
        workspace_id=workspace_id,
        name="F&B Marketing",
        slug="fb-marketing",
        status=EntityStatus.ACTIVE,
        created_at=now,
        updated_at=now,
    )

    def fake_get_project(*, project_id, uow):
        return project

    monkeypatch.setattr(
        projects_v2,
        "get_project",
        fake_get_project,
    )

    response = projects_v2.read_project(
        project_id=project_id,
        uow=object(),
    )

    assert response.id == project_id
    assert response.workspace_id == workspace_id
    assert response.name == "F&B Marketing"
    assert response.slug == "fb-marketing"
    assert response.status == EntityStatus.ACTIVE
    assert response.created_at == now
    assert response.updated_at == now


def test_read_project_maps_not_found_to_http_404(
    monkeypatch: pytest.MonkeyPatch,
):
    project_id = uuid4()

    def fake_get_project(*, project_id, uow):
        raise ProjectNotFoundError(
            f"Project '{project_id}' was not found."
        )

    monkeypatch.setattr(
        projects_v2,
        "get_project",
        fake_get_project,
    )

    with pytest.raises(HTTPException) as exc_info:
        projects_v2.read_project(
            project_id=project_id,
            uow=object(),
        )

    assert exc_info.value.status_code == 404
    assert str(project_id) in exc_info.value.detail


def test_create_project_route_returns_created_project_id(
    monkeypatch: pytest.MonkeyPatch,
):
    workspace_id = uuid4()
    project_id = uuid4()

    def fake_create_project(*, command, uow):
        assert command.workspace_id == workspace_id
        assert command.name == "Gà Ủ Muối Campaign"
        assert command.slug == "ga-u-muoi-campaign"

        return project_id

    monkeypatch.setattr(
        projects_v2,
        "create_project",
        fake_create_project,
    )

    response = projects_v2.create_project_route(
        request=CreateProjectRequest(
            workspace_id=workspace_id,
            name="Gà Ủ Muối Campaign",
            slug="ga-u-muoi-campaign",
        ),
        uow=object(),
    )

    assert response.id == project_id


def test_create_project_route_maps_missing_workspace_to_http_404(
    monkeypatch: pytest.MonkeyPatch,
):
    workspace_id = uuid4()

    def fake_create_project(*, command, uow):
        raise WorkspaceNotFoundError(
            f"Workspace '{workspace_id}' was not found."
        )

    monkeypatch.setattr(
        projects_v2,
        "create_project",
        fake_create_project,
    )

    with pytest.raises(HTTPException) as exc_info:
        projects_v2.create_project_route(
            request=CreateProjectRequest(
                workspace_id=workspace_id,
                name="Campaign",
                slug="campaign",
            ),
            uow=object(),
        )

    assert exc_info.value.status_code == 404
    assert str(workspace_id) in exc_info.value.detail


def test_create_project_route_maps_slug_conflict_to_http_409(
    monkeypatch: pytest.MonkeyPatch,
):
    workspace_id = uuid4()

    def fake_create_project(*, command, uow):
        raise ProjectSlugConflictError(
            "A project with slug 'campaign' already exists."
        )

    monkeypatch.setattr(
        projects_v2,
        "create_project",
        fake_create_project,
    )

    with pytest.raises(HTTPException) as exc_info:
        projects_v2.create_project_route(
            request=CreateProjectRequest(
                workspace_id=workspace_id,
                name="Campaign",
                slug="campaign",
            ),
            uow=object(),
        )

    assert exc_info.value.status_code == 409
    assert "campaign" in exc_info.value.detail