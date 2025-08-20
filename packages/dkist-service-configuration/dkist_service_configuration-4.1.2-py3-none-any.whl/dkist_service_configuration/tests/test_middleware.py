"""Test middleware for DKIST service configuration."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.fixture
def fastapi_app():
    """Fixture to create a FastAPI app for testing."""
    app = FastAPI()

    @app.get("/health", status_code=200)
    def health():
        return {"status": "ok"}

    @app.get("/foo", status_code=200)
    def foo():
        return {"status": "ok"}

    return app


@pytest.fixture()
def api_client(fastapi_app) -> TestClient:
    return TestClient(fastapi_app)


def test_add_fastapi_middleware(instrumented_mesh_config, fastapi_app, api_client):
    """Test that the DKIST middleware can be added to a FastAPI app."""
    instrumented_mesh_config.add_fastapi_middleware(app=fastapi_app)
    response = api_client.get("/health")
    assert response.status_code == 200
    response = api_client.get("/foo")
    assert response.status_code == 200
    response = api_client.get("/foo?bar=baz")
    assert response.status_code == 200
