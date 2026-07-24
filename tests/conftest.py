import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

from app.db import get_db
from app.main import app


@pytest.fixture
def client():
    """
    FastAPI test client with the real get_db dependency overridden by a
    mock session. Route tests should verify request/response behavior,
    not require a live Postgres connection — that would make fast unit
    tests dependent on external infrastructure being up and reachable.
    """
    app.dependency_overrides[get_db] = lambda: MagicMock()
    yield TestClient(app)
    app.dependency_overrides.clear()