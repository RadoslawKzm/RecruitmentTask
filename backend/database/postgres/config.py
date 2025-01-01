import os

from loguru import logger

"""
This module configures PostgreSQL settings,
using environment variables if available,
or defaults to predefined values for local development.
"""

POSTGRES_USER: str = os.getenv("POSTGRES_USER") or "postgres"
POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD") or "postgres"
POSTGRES_HOSTNAME: str = os.getenv("POSTGRES_HOSTNAME") or "localhost"
POSTGRES_PORT: int = os.getenv("POSTGRES_PORT") or 5432
POSTGRES_DB: str = os.getenv("POSTGRES_DB") or "RecruitmentTask"
POSTGRES_SYNC: str = "postgresql+psycopg2"
POSTGRES_ASYNC: str = "postgresql+asyncpg"

logger.info(f"{POSTGRES_USER=}")
logger.info(f"{POSTGRES_PASSWORD=}")
logger.info(f"{POSTGRES_HOSTNAME=}")
logger.info(f"{POSTGRES_PORT=}")
logger.info(f"{POSTGRES_DB=}")
POSTGRES_SYNC_URL: str = (
    f"{POSTGRES_SYNC}://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
    f"{POSTGRES_HOSTNAME}:{POSTGRES_PORT}/{POSTGRES_DB}"
)
POSTGRES_ASYNC_URL: str = (
    f"{POSTGRES_ASYNC}://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
    f"{POSTGRES_HOSTNAME}:{POSTGRES_PORT}/{POSTGRES_DB}"
)
