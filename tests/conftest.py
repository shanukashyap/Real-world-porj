import pytest


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "integration: hits real Postgres + optional model download"
    )


@pytest.fixture
def anyio_backend():
    return "asyncio"
