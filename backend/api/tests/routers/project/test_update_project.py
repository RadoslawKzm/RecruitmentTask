from datetime import datetime
from unittest.mock import AsyncMock

import fastapi
import pytest
from fastapi.testclient import TestClient

from backend.api.tests.routers.project.data_for_test import (
    edit_in_db_1,
    flattened_geojson,
)


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


@pytest.mark.parametrize(
    "status_code",
    [
        fastapi.status.HTTP_200_OK,
        fastapi.status.HTTP_204_NO_CONTENT,
        fastapi.status.HTTP_404_NOT_FOUND,
    ],
)
@pytest.mark.asyncio
async def test_update_project(
    mock_session,
    mocker,
    status_code,
    sync_client: TestClient,
):
    mock_core_edit = mocker.patch(
        "backend.core.core.edit_in_db",
        AsyncMock(return_value=status_code),
    )
    project_id = 12
    name = "Project 69"
    start_date = "1920-05-18T00:00:00"
    end_date = "2005-04-02T00:00:00"
    description = "Simplicity is the ultimate sophistication"
    response = sync_client.put(
        url=f"/project/{project_id}",
        params={
            "name": name,
            "date_range": [start_date, end_date],
            "description": description,
        },
        json=edit_in_db_1,
    )
    assert response.status_code == status_code
    mock_core_edit.assert_called_once_with(
        session=mock_session,
        project_id=project_id,
        name=name,
        description=description,
        start_date=datetime.fromisoformat(start_date),
        end_date=datetime.fromisoformat(end_date),
        flattened_geojson=flattened_geojson,
    )


def test_update_project_too_big_id(sync_client: TestClient):
    project_id = 9999999
    name = "Project 69"
    start_date = "1920-05-18T00:00:00"
    end_date = "2005-04-02T00:00:00"
    description = "Simplicity is the ultimate sophistication"
    response = sync_client.put(
        url=f"/project/{project_id}",
        params={
            "name": name,
            "date_range": [start_date, end_date],
            "description": description,
        },
        json=edit_in_db_1,
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": "Request validation failed",
        "type": "less_than_equal",
        "loc": ["path", "project_id"],
        "msg": "Input should be less than or equal to 999999",
        "input": "9999999",
        "ctx": {"le": 999999},
    }


def test_update_project_negative_id(sync_client: TestClient):
    project_id = -1
    name = "Project 69"
    start_date = "1920-05-18T00:00:00"
    end_date = "2005-04-02T00:00:00"
    description = "Simplicity is the ultimate sophistication"
    response = sync_client.put(
        url=f"/project/{project_id}",
        params={
            "name": name,
            "date_range": [start_date, end_date],
            "description": description,
        },
        json=edit_in_db_1,
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": "Request validation failed",
        "type": "greater_than_equal",
        "loc": ["path", "project_id"],
        "msg": "Input should be greater than or equal to 0",
        "input": "-1",
        "ctx": {"ge": 0},
    }


def test_read_project_missing_id(sync_client: TestClient):
    response = sync_client.put("/project/")
    assert response.status_code == 405
    assert response.json() == {"detail": "Method Not Allowed"}


def test_update_project_name_too_big(sync_client: TestClient):
    project_id = 12
    name = "NameOver32CharactersForTestingStuff"
    start_date = "1920-05-18T00:00:00"
    end_date = "2005-04-02T00:00:00"
    description = "Simplicity is the ultimate sophistication"
    response = sync_client.put(
        url=f"/project/{project_id}",
        params={
            "name": name,
            "date_range": [start_date, end_date],
            "description": description,
        },
        json=edit_in_db_1,
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": "Request validation failed",
        "type": "string_too_long",
        "loc": ["query", "name"],
        "msg": "String should have at most 32 characters",
        "input": "NameOver32CharactersForTestingStuff",
        "ctx": {"max_length": 32},
    }
