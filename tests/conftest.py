import os

import pytest

# Integration tests run when Postgres is available (e.g. Docker Compose).
INTEGRATION = os.getenv("INTEGRATION_TESTS", "").lower() in ("1", "true", "yes")


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "integration: hits real Postgres + optional model download"
    )


@pytest.fixture
def anyio_backend():
    return "asyncio"
