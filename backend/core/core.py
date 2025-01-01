import hashlib
import json
from datetime import datetime
from typing import Annotated, Any, Optional

import pydantic
from fastapi import status
from loguru import logger
from sqlalchemy.orm import joinedload
from sqlmodel import delete, func, select

from backend.core import core_models
from backend.database.postgres import project_models

PROJECT_ID = int


def dict_hash(d):
    return hashlib.sha256(
        json.dumps(d, sort_keys=True).encode("utf-8")
    ).hexdigest()


# @pydantic.validate_call
async def read_from_db(
    *,
    session: Any,  # AsyncSession
    project_id: Annotated[
        int,
        pydantic.Field(
            ge=0,
            le=999999,
            description="Project ID cannot be lower than 0",
        ),
    ],
) -> core_models.ProjectCore | int:
    logger.debug("Reading project data from db")
    # statement = select(project_models.Project).where(
    #     project_models.Project.project_id == project_id
    # )
    statement = (
        select(project_models.Project)
        .where(project_models.Project.project_id == project_id)
        .options(
            joinedload(project_models.Project.geojson)
            .joinedload(project_models.GeoJson.geometry)
            .joinedload(project_models.Geometry.coordinates)
        )
    )
    res = await session.execute(statement)
    result = res.scalar()
    if not result:
        return status.HTTP_404_NOT_FOUND
    return core_models.ProjectCore.model_validate(result)


# @pydantic.validate_call
async def delete_from_db(
    *,
    session: Any,  # AsyncSession
    project_id: Annotated[
        int,
        pydantic.Field(
            ge=0,
            le=999999,
            description="Project ID cannot be lower than 0",
        ),
    ],
    commit: Optional[bool] = True,
) -> int:
    statement = delete(project_models.Project).where(
        project_models.Project.project_id == project_id  # noqa
    )
    result = await read_from_db(session=session, project_id=project_id)
    if result == status.HTTP_404_NOT_FOUND:
        return status.HTTP_404_NOT_FOUND
    try:
        await session.execute(statement)
        if commit:
            await session.commit()
    except Exception as exc_info:  # noqa: F841
        logger.opt(lazy=True).exception(
            "Failed to delete project data: {x}",
            x=lambda: f"{project_id}, error info: {exc_info}",  # noqa: F821
        )
    return status.HTTP_200_OK


@pydantic.validate_call
async def add_to_db(
    *,
    session: Any,  # AsyncSession
    __project_id: Annotated[  # For use only with edit
        Optional[int],
        pydantic.Field(
            ge=0,
            le=999999,
            description="Project ID cannot be lower than 0",
        ),
    ] = None,
    name: str,
    start_date: datetime,
    end_date: datetime,
    description: Optional[str] = None,
    flattened_geojson: core_models.GeoJson,
    commit: Optional[bool] = True,
) -> PROJECT_ID:
    logger.debug("Adding geojson to db")
    logger.debug(
        f"New project: {name=}, {start_date=},{end_date=} {description=}"
    )
    project = project_models.Project(
        name=name,
        start_date=start_date,
        end_date=end_date,
        description=description,
    )
    if __project_id:
        # use only with edit, which first removes given id
        project.project_id = __project_id
    session.add(project)
    await session.flush()
    geo_json = project_models.GeoJson(
        project_id=project.project_id,
        type=flattened_geojson.type,
    )
    session.add(geo_json)
    await session.flush()
    geometry = project_models.Geometry(
        geojson_id=geo_json.geojson_id,
        type=flattened_geojson.geometry.type,
    )
    session.add(geometry)
    await session.flush()

    coordinates = [
        project_models.Coordinate(
            geometry_id=geometry.geometry_id,
            latitude=coordinate.latitude,
            longitude=coordinate.longitude,
        )
        for coordinate in flattened_geojson.geometry.coordinates
    ]
    session.add_all(coordinates)
    if commit:
        await session.commit()
        await session.refresh(project)
        logger.debug(f"Added successfully. Project ID: {project.project_id}")
    return project.project_id


@pydantic.validate_call
async def edit_in_db(
    *,
    session: Any,  # AsyncSession
    project_id: Annotated[
        int,
        pydantic.Field(
            ge=0,
            le=999999,
            description="Project ID cannot be lower than 0",
        ),
    ],
    name: str,
    start_date: datetime,
    end_date: datetime,
    description: Optional[str] = None,
    flattened_geojson: core_models.GeoJson,
) -> int | bool:
    logger.debug("Reading project data from db")
    statement = select(project_models.Project).where(
        project_models.Project.project_id == project_id
    )
    res = await session.execute(statement)
    res_scalar = res.scalar()
    if not res_scalar:
        logger.opt(lazy=True).debug(
            "Project ID:{x} not found",
            x=lambda: project_id,
        )
        return status.HTTP_404_NOT_FOUND
    result = core_models.ProjectCore.model_validate(res_scalar)
    inputs_dict: dict = {
        "name": name,
        "start_date": str(start_date),
        "end_date": str(end_date),
        "description": description,
        "geojson": flattened_geojson.model_dump(),
    }
    results_dict: dict = {
        "name": result.name,
        "start_date": str(result.start_date),
        "end_date": str(result.end_date),
        "description": result.description,
        "geojson": result.geojson.model_dump(),
    }

    if dict_hash(inputs_dict) == dict_hash(results_dict):
        # Dicts are the same, no changes
        return status.HTTP_204_NO_CONTENT
    await delete_from_db(session=session, project_id=project_id, commit=False)
    await add_to_db(
        session=session,
        __project_id=project_id,
        name=name,
        start_date=start_date,
        end_date=end_date,
        description=description,
        flattened_geojson=flattened_geojson,
        commit=False,
    )
    await session.commit()
    return status.HTTP_200_OK


# @pydantic.validate_call
async def fetch_all_projects(
    *,
    session: Any,  # AsyncSession
    page: Annotated[int, pydantic.Field(ge=0, default=0)] = 0,
    size: Annotated[int, pydantic.Field(ge=1, le=100, default=10)] = 10,
):
    statement = (
        select(project_models.Project)
        .order_by(project_models.Project.project_id)
        .offset(page * size)
        .limit(size)
        .options(
            joinedload(project_models.Project.geojson)
            .joinedload(project_models.GeoJson.geometry)
            .joinedload(project_models.Geometry.coordinates)
        )
    )

    res = await session.execute(statement)
    results = res.unique().scalars().all()
    if not results:
        return status.HTTP_404_NOT_FOUND
    # return result
    return [
        core_models.ProjectCore.model_validate(result) for result in results
    ]


# @pydantic.validate_call
async def get_projects_count(session: Any) -> int:
    statement = select(func.count(project_models.Project.project_id))
    result = await session.execute(statement)
    return result.scalar()
