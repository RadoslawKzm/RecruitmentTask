import typing
from datetime import datetime

import pydantic
from fastapi import (
    APIRouter,
    Body,
    HTTPException,
    Path,
    Query,
    Response,
    status,
)
from fastapi.responses import JSONResponse
from loguru import logger

from backend.api.routers.project import validators
from backend.api.routers.project.models import (
    ProjectProtocol,
    request_models,
    response_models,
)
from backend.api.routers.project.swagger_examples import request_examples
from backend.api.routers.project.swagger_examples.response_examples import (
    get_project_example,
)
from backend.core import core
from backend.database.postgres.session import DBSessionDep

router = APIRouter(prefix="/project", tags=["project"])


@router.get(
    "/{project_id}",
    responses={
        404: {
            "content": {
                "application/json": {
                    "example": "Project ID: {project_id} Not Found"
                }
            },
        },
        200: {
            "description": "Item requested by ID",
            "content": {"application/json": get_project_example},
        },
    },
)
async def read_project(
    session: DBSessionDep,
    project_id: typing.Annotated[
        int,
        Path(
            ...,
            ge=0,
            le=999999,
            openapi_examples=request_examples.project_id,
        ),
    ],
) -> response_models.ProjectResponse:
    """
    @TODO Pagination if geojson is too big
    Returns the details of a project from the database
        with the specified Project ID
    - `project_id` INT: min: **0**, max: **999,999**

    <!--
    Retrieve a project by its ID.

    :param session:
        The database session dependency used to interact with the database.
    :type session: DBSessionDep

    :param project_id:
        The unique identifier of the project to retrieve.
        Must be a positive integer between 0 and 999,999.
    :type project_id: int

    :return:
        A response model containing the details of the requested project:
        - **project_id** (*int*): The ID of the retrieved project.v
        - **name** (*str*): The name of the project.
        - **description** (*str*): A detailed description of the project.
        - **date_range** (*tuple[datetime.date, datetime.date]*):
                The start and end dates of the project.
        - **geojson** (*dict*): Geospatial data in GeoJSON format.
    :rtype: response_models.ProjectResponse

    :raises HTTPException:
        - **404 Not Found**: If no project is found with the specified ID.
        - **400 Bad Request**: If the `project_id` is invalid
                                or out of the allowed range.
    """
    logger.debug(f"read project id {project_id}")
    result: ProjectProtocol | int = await core.read_from_db(
        session=session,
        project_id=project_id,
    )
    if result == status.HTTP_404_NOT_FOUND:
        logger.opt(lazy=True).info(
            "Project id {project_id} not found",
            project_id=lambda: f"{project_id}",
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project ID: {project_id} Not Found",
        )
    logger.opt(lazy=True).info(
        "Returning project details of project id: {x}",
        x=lambda: f"{project_id}",
    )
    return response_models.ProjectResponse(
        project_id=result.project_id,
        name=result.name,
        description=result.description,
        date_range=(result.start_date, result.end_date),
        geojson=result.geojson,  # noqa
    )


@router.put(
    "/{project_id}",
    responses={
        200: {"description": "Item Updated"},
        204: {"description": "No changes made"},
        404: {
            "content": {
                "application/json": {
                    "example": "Project ID: {project_id} Not Found"
                }
            },
        },
    },
)
async def update_project(
    session: DBSessionDep,
    project_id: typing.Annotated[
        int,
        Path(
            ...,
            ge=0,
            le=999999,
            openapi_examples=request_examples.project_id,
        ),
    ],
    name: typing.Annotated[
        str,
        Query(
            ...,
            min_length=1,
            max_length=32,
            description="Name must be a string "
            "with a maximum length of 32 characters.",
            openapi_examples=request_examples.name,
        ),
        pydantic.AfterValidator(validators.name_validator),
    ],
    date_range: typing.Annotated[
        tuple[datetime, datetime],
        Query(
            ...,
            max_length=2,
            description="ISO 8601 format: 2008-09-15T15:53:00+05:00",
            openapi_examples=request_examples.date_range,
        ),
        pydantic.AfterValidator(validators.date_validator),
    ],
    geo_json: typing.Annotated[
        request_models.GeoJson,
        Body(
            ...,
            openapi_examples=request_examples.geojson_request_example,
        ),
    ],
    description: typing.Annotated[
        typing.Optional[str],
        Query(
            min_length=0,
            max_length=100,
            description="An optional description of the name.",
            openapi_examples=request_examples.description,
        ),
    ] = None,
) -> Response:
    """
    Update an existing project by its ID.
    - `project_id` INT: min: **0**, max: **999,999**
    - `name` STR: character limit **32**
    - `date_range`: max: **Current date**
    - `description` STR: character limit **100**
    - `Body` JSON:


    <!--
    This endpoint allows updating the details of an existing project.
    All required parameters must be provided to successfully update the project

    :param session:
        The database session dependency used to interact with the database.
    :type session: DBSessionDep

    :param project_id:
        The unique identifier of the project to update.
        Must be a positive integer between 0 and 999,999.
    :type project_id: int

    :param name:
        The new name for the project.
        String with a minimum length=1 and a maximum length=32 characters
    :type name: str

    :param date_range:
        The new start and end dates for the project.
        Must be provided as a tuple of two ISO 8601-formatted datetime strings
        (e.g., `2008-09-15T15:53:00+05:00`).
    :type date_range: tuple[datetime, datetime]

    :param geo_json:
        The updated geospatial data in GeoJSON format.
        Must adhere to the `request_models.GeoJson` structure.
    :type geo_json: request_models.GeoJson

    :param description:
        An optional description for the project.
        If provided, it must be a string with a maximum length=100 characters.
    :type description: typing.Optional[str]

    :return:
        No content is returned on success (HTTP 204).
    :rtype: Response

    :raises HTTPException:
        - **400 Bad Request**: If any of the provided parameters are invalid.
        - **404 Not Found**: If no project is found with the specified ID.
        - **422 Unprocessable Entity**: If the request body
                                            or query parameters fail validation
    """

    logger.debug("put endpoint doing idempotent stuff")
    result: bool = await core.edit_in_db(
        session=session,
        project_id=project_id,
        name=name,
        description=description,
        start_date=date_range[0],
        end_date=date_range[1],
        flattened_geojson=geo_json.model_flatten(),  # noqa
        # validator needs core model to validate dict matching model
        # if Model|dict then if model doesn't match,
        # validator tries dict so {} will fly
    )
    if result == status.HTTP_404_NOT_FOUND:
        logger.opt(lazy=True).info(
            "Project id {project_id} not found",
            project_id=lambda: f"{project_id}",
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project ID: {project_id} Not Found",
        )
    if result == status.HTTP_204_NO_CONTENT:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    return Response(status_code=status.HTTP_200_OK)


@router.delete(
    "/{project_id}",
    responses={
        200: {
            "description": "Item requested by ID",
            "content": {"application/json": {"example": "string"}},
        },
        404: {
            "content": {
                "application/json": {
                    "example": "Project ID: {project_id} Not Found"
                }
            },
        },
    },
)
async def delete_project(
    session: DBSessionDep,
    project_id: typing.Annotated[
        int,
        Path(
            ...,
            ge=0,
            le=999999,
            openapi_examples=request_examples.project_id,
        ),
    ],
) -> Response:
    """
    Delete a project by its ID.
    - `project_id` INT: min: **0**, max: **999,999**

    <!--
    This endpoint deletes the project with the specified ID from the database.
    The `project_id` must be within the range of 0 to 999,999.

    :param session:
        The database session dependency used to interact with the database.
    :type session: DBSessionDep

    :param project_id:
        The unique identifier of the project to delete.
        Must be a positive integer between 0 and 999,999.
    :type project_id: int

    :return:
        A boolean indicating whether the project was successfully deleted.
        Returns `True` if the project was found and deleted, otherwise `False`
    :rtype: bool

    :raises HTTPException:
        - **404 Not Found**: If no project is found with the specified ID.
        - **400 Bad Request**: If the `project_id` is invalid
                                or out of the allowed range.
    """
    logger.debug("Deleting project: {project_id}")
    result: int = await core.delete_from_db(
        session=session,
        project_id=project_id,
    )
    if result == status.HTTP_404_NOT_FOUND:
        logger.opt(lazy=True).info(
            "Project id {project_id} not found",
            project_id=lambda: f"{project_id}",
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project ID: {project_id} Not Found",
        )
    logger.debug("Successfully deleted project: {project_id}")
    return Response(status_code=status.HTTP_200_OK)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {
            "description": "Project Created",
            "content": {
                "application/json": {"example": {"Project_id": "{project_id}"}}
            },
        },
    },
)
async def create_project(
    session: DBSessionDep,
    name: typing.Annotated[
        str,
        Query(
            ...,
            min_length=1,
            max_length=32,
            description="Name must be a string"
            " with a maximum length of 32 characters.",
            openapi_examples=request_examples.name,
        ),
        pydantic.AfterValidator(validators.name_validator),
    ],
    date_range: typing.Annotated[
        tuple[datetime, datetime],
        Query(
            ...,
            max_length=2,
            description="ISO 8601 format: 2008-09-15T15:53:00+05:00",
            openapi_examples=request_examples.date_range,
        ),
        pydantic.AfterValidator(validators.date_validator),
    ],
    description: typing.Annotated[
        str,
        Query(
            min_length=0,
            max_length=100,
            description="An optional description of the name.",
            openapi_examples=request_examples.description,
        ),
    ],
    geo_json: typing.Annotated[
        request_models.GeoJson,
        Body(
            ...,
            openapi_examples=request_examples.geojson_request_example,
        ),
    ],
):
    """
    Create a new project.
    - `name` STR: character limit **32**
    - `date_range`: max: **Current date**
    - `description` STR: character limit **100**
    - `Body` JSON:

    <!--
    This endpoint creates a new project with the provided details.
    All required parameters must be provided to successfully create the project

    :param session:
        The database session dependency used to interact with the database.
    :type session: DBSessionDep

    :param name:
        The name of the project.
        Must be a string, minimum length=1 and a maximum length=32 characters.
    :type name: str

    :param date_range:
        The start and end dates for the project.
        Must be provided as a tuple of two ISO 8601-formatted datetime strings
        (e.g., `2008-09-15T15:53:00+05:00`).
    :type date_range: tuple[datetime, datetime]

    :param description:
        An optional description for the project.
        If provided, must be string with a maximum length of 100 characters.
    :type description: str

    :param geo_json:
        The geospatial data for the project in GeoJSON format.
        Must adhere to the `request_models.GeoJson` structure.
    :type geo_json: request_models.GeoJson

    :return:
        A JSON response containing the details of the newly created project.
        The response includes the `project_id` of the created project.
    :rtype: JSONResponse

    :raises HTTPException:
        - **400 Bad Request**: If any of the provided parameters are invalid.
        - **422 Unprocessable Entity**:
                If the request body or query parameters fail validation.
    """
    project_id: int = await core.add_to_db(
        session=session,
        name=name,
        start_date=date_range[0],
        end_date=date_range[1],
        description=description,
        flattened_geojson=geo_json.model_flatten(),  # noqa
        # validator needs core model to validate dict matching model
        # if Model|dict then if model doesn't match,
        # validator tries dict so {} will fly
    )
    logger.debug(f"Created project with ID: {project_id}")
    return JSONResponse(
        content={"Project_id": project_id},
        status_code=status.HTTP_201_CREATED,
    )
