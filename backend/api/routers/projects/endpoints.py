import math
import random
from typing import Annotated

from fastapi import APIRouter, Query, Response, status

from backend.api.routers.project.models import response_models
from backend.api.routers.project.models.protocols import Project
from backend.core import core
from backend.database.postgres.session import DBSessionDep

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/list", status_code=200)
async def list_projects(
    response: Response,
    session: DBSessionDep,
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=100)] = 10,
) -> list[response_models.ProjectResponse]:
    """
    Returns a paginated list of projects.
    - `page`: Current page number (default 1).
    - `size`: Number of items per page (default 10, max 100).

    <!--
    List all projects
    :param response: Coming from FastAPI to set headers in response.
    :type response: Response
    :param session: Coming from FastAPI dependency.
    :type AsyncSession:
    :param page: Number of page (default 1).
    :type page: Annotated[int, Query(ge=1)]
    :param size: Size of each page (default 10).
    :type size: Annotated[int, Query(ge=1, le=100)]
    :return: List of projects.
    :rtype: list[response_models.ProjectResponse]
    """
    int_page = page - 1
    projects: list[Project] = await core.fetch_all_projects(
        session=session,
        page=int_page,
        size=size,
    )
    if projects == status.HTTP_404_NOT_FOUND:
        response_code: int = random.choice(
            [
                status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS,
                status.HTTP_418_IM_A_TEAPOT,
            ],
        )
        return Response(status_code=response_code)
    # Convert database records to response model
    project_responses = [
        response_models.ProjectResponse(
            project_id=project.project_id,
            name=project.name,
            description=project.description,
            date_range=(project.start_date, project.end_date),
            geojson=project.geojson,  # noqa
        )
        for project in projects
    ]
    total_projects: int = await core.get_projects_count(session=session)
    last_page: int = math.ceil(total_projects / size)
    # Paginate results
    link = (
        f"/api/projects/list?page={page}&size={size}; "
        f'rel="prev", /api/projects/list?page={page-1}&size={size}; '
        f'rel="next", /api/projects/list?page={page+1}&size={size}; '
        f'rel="first, /api/projects/list?page={1}&size={size}; '
        f'rel="last, /api/projects/list?page={last_page}&size={size}"'
    )
    response.headers["Link"] = link
    response.headers["X-Page"] = str(page)
    response.headers["X-Size"] = str(size)

    return project_responses
