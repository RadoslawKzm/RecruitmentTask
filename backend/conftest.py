import pytest

# from httpx import AsyncClient
# from backend.api.app import app
from fastapi.testclient import TestClient

from backend.loguru_logger.logger_setup import logger_setup


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    """
    Runs once at the start of the pytest session.
    """
    logger_setup()


# from httpx import AsyncClient
# @pytest.fixture
# async def async_client():
#     """
#     If needed async client to better mimic prod environment
#     """
#     async with AsyncClient(app=app, base_url="http://test") as client:
#         yield client


@pytest.fixture(scope="session")
def sync_client():
    # with TestClient(app=app) as client:
    #     yield client
    # client = TestClient(app)
    # return client
    from backend.api.app import app

    return TestClient(app)
