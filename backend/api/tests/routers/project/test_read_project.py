from datetime import datetime
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from backend.api.tests.routers.project.data_for_test import read_from_db_1


@pytest.fixture
def mock_session(mocker):
    async_mock = AsyncMock()
    async_mock.__aenter__.return_value = async_mock
    async_mock.__aexit__.return_value = None  # Mock the exit
    mocker.patch(
        "backend.database.postgres.session.DbContext",
        return_value=async_mock,
    )
    return async_mock


@pytest.mark.asyncio
async def test_read_project_success(
    mock_session,
    mocker,
    sync_client: TestClient,
):
    mocker.patch(
        "backend.core.core.read_from_db",
        AsyncMock(return_value=read_from_db_1),
    )

    response = sync_client.get("/project/1")
    assert response.status_code == 200
    data = response.json()
    assert data["project_id"] == read_from_db_1.project_id
    assert data["name"] == read_from_db_1.name
    assert data["description"] == read_from_db_1.description
    data_start_date = datetime.fromisoformat(data["date_range"][0])
    assert data_start_date == read_from_db_1.start_date
    data_end_date = datetime.fromisoformat(data["date_range"][1])
    assert data_end_date == read_from_db_1.end_date
    assert data["geojson"] == read_from_db_1.geojson.model_dump()


@pytest.mark.asyncio
async def test_read_project_not_found(
    mock_session,
    mocker,
    sync_client: TestClient,
):
    mocker.patch(
        "backend.core.core.read_from_db",
        AsyncMock(return_value=404),
    )
    response = sync_client.get("/project/9999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Project ID: 9999 Not Found"}


@pytest.mark.asyncio
async def test_read_project_bad_input_type(
    mock_session,
    sync_client: TestClient,
):
    response = sync_client.get("/project/test")
    assert response.status_code == 422
    assert response.json() == {
        "detail": "Request validation failed",
        "type": "int_parsing",
        "loc": ["path", "project_id"],
        "msg": "Input should be a valid integer, "
        "unable to parse string as an integer",
        "input": "test",
    }


@pytest.mark.asyncio
async def test_read_project_too_big_id(mock_session, sync_client: TestClient):
    response = sync_client.get("/project/9999999")
    assert response.status_code == 422
    assert response.json() == {
        "detail": "Request validation failed",
        "type": "less_than_equal",
        "loc": ["path", "project_id"],
        "msg": "Input should be less than or equal to 999999",
        "input": "9999999",
        "ctx": {"le": 999999},
    }


@pytest.mark.asyncio
async def test_read_project_negative_id(mock_session, sync_client: TestClient):
    response = sync_client.get("/project/-1")
    assert response.status_code == 422
    assert response.json() == {
        "detail": "Request validation failed",
        "type": "greater_than_equal",
        "loc": ["path", "project_id"],
        "msg": "Input should be greater than or equal to 0",
        "input": "-1",
        "ctx": {"ge": 0},
    }


@pytest.mark.asyncio
async def test_read_project_missing_id(mock_session, sync_client: TestClient):
    response = sync_client.get("/project/")
    assert response.status_code == 405
    assert response.json() == {"detail": "Method Not Allowed"}
