from main import app


def test_project_v2_routes_are_mounted_with_legacy_routes():
    paths = app.openapi()["paths"]

    assert "post" in paths["/api/v2/projects/"]
    assert "get" in paths["/api/v2/projects/{project_id}"]

    assert "/api/projects/{project_id}/init" in paths
    assert "/api/generate/business-data" in paths