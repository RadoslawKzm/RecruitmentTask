from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from loguru import logger

from backend.api.routers.about import response_examples

router = APIRouter(prefix="/info", tags=["about"])


@router.get("/", status_code=200, responses=response_examples.about)
async def about() -> JSONResponse:
    logger.debug("about")
    return JSONResponse(
        content={"data": "version_v1"}, status_code=status.HTTP_200_OK
    )
