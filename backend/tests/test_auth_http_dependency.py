from uuid import uuid4

from fastapi.testclient import TestClient

from api.dependencies.auth import (
    get_access_token_verifier,
)
from infrastructure.database.session import get_db
from main import app


def test_missing_bearer_token_returns_401_before_verifier_is_built():
    def fake_db():
        yield object()

    def fail_if_verifier_is_built():
        raise AssertionError(
            "Verifier must not be built without credentials."
        )

    app.dependency_overrides[get_db] = fake_db
    app.dependency_overrides[
        get_access_token_verifier
    ] = fail_if_verifier_is_built

    try:
        client = TestClient(app)

        response = client.get(
            f"/api/v2/projects/{uuid4()}",
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Authentication is required.",
    }
    assert response.headers["www-authenticate"] == "Bearer"