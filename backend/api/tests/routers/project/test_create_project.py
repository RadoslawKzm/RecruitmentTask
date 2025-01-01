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


@pytest.mark.asyncio
async def test_create_project(mock_session, mocker, sync_client: TestClient):
    status_code = fastapi.status.HTTP_201_CREATED
    project_id = 12
    mock_core_edit = mocker.patch(
        "backend.core.core.add_to_db",
        AsyncMock(return_value=project_id),
    )
    name = "Project 69"
    start_date = "1920-05-18T00:00:00"
    end_date = "2005-04-02T00:00:00"
    description = "Simplicity is the ultimate sophistication"
    response = sync_client.post(
        url="/project/",
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
        name=name,
        description=description,
        start_date=datetime.fromisoformat(start_date),
        end_date=datetime.fromisoformat(end_date),
        flattened_geojson=flattened_geojson,
    )
    assert response.json() == {"Project_id": project_id}


def test_create_project_name_too_big(sync_client: TestClient):
    name = "NameOver32CharactersForTestingStuff"
    start_date = "1920-05-18T00:00:00"
    end_date = "2005-04-02T00:00:00"
    description = "Simplicity is the ultimate sophistication"
    response = sync_client.post(
        url="/project/",
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
