from datetime import datetime, timezone
from uuid import uuid4

import pytest
from fastapi import HTTPException

from api.routes import projects_v2
from application.projects.dto import ProjectView
from application.projects.queries import ProjectNotFoundError
from modules.common.enums import EntityStatus


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