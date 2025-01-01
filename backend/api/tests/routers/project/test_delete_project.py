from unittest.mock import AsyncMock

import pytest
from fastapi import status
from fastapi.testclient import TestClient


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
    "status_code, expected_response",
    [
        (status.HTTP_200_OK, status.HTTP_200_OK),
        (status.HTTP_404_NOT_FOUND, status.HTTP_404_NOT_FOUND),
    ],
)
@pytest.mark.asyncio
async def test_delete_project(
    mock_session,
    mocker,
    status_code,
    expected_response,
    sync_client: TestClient,
):
    mock_core_delete = mocker.patch(
        "backend.core.core.delete_from_db",
        AsyncMock(return_value=status_code),
    )

    project_id = 12
    response = sync_client.delete(f"/project/{project_id}")

    assert response.status_code == expected_response
    mock_core_delete.assert_called_once_with(
        session=mock_session,
        project_id=project_id,
    )


def test_delete_project_too_big_id(sync_client: TestClient):
    response = sync_client.delete("/project/9999999")
    assert response.status_code == 422
    assert response.json() == {
        "detail": "Request validation failed",
        "type": "less_than_equal",
        "loc": ["path", "project_id"],
        "msg": "Input should be less than or equal to 999999",
        "input": "9999999",
        "ctx": {"le": 999999},
    }


def test_delete_project_negative_id(sync_client: TestClient):
    response = sync_client.delete("/project/-1")
    assert response.status_code == 422
    assert response.json() == {
        "detail": "Request validation failed",
        "type": "greater_than_equal",
        "loc": ["path", "project_id"],
        "msg": "Input should be greater than or equal to 0",
        "input": "-1",
        "ctx": {"ge": 0},
    }


def test_delete_project_missing_id(sync_client: TestClient):
    response = sync_client.delete("/project/")
    assert response.status_code == 405
    assert response.json() == {"detail": "Method Not Allowed"}
