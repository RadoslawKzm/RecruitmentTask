import random

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from loguru import logger

from backend.api.routers.healthcheck import response_examples

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/", status_code=200, responses=response_examples.health)
async def health() -> JSONResponse:
    logger.debug("healthcheck")
    responses = [
        "I am Groot",
        "This is the way",
        "Luke, I am your father",
        "Hodor...",
    ]
    return JSONResponse(
        content={"data": random.choice(responses)},
        status_code=status.HTTP_200_OK,
    )
