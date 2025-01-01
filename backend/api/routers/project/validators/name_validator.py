import fastapi
from loguru import logger


def name_validator(name: str) -> str:
    if not name.strip():  # Ensure the name is not only whitespace
        logger.opt(lazy=True).debug(
            "{x}",
            x=lambda: f"{name=} cannot be empty or consist only of whitespace",
        )
        raise fastapi.HTTPException(
            status_code=422,
            detail="Name cannot be empty or consist only of whitespace.",
        )
    return name
