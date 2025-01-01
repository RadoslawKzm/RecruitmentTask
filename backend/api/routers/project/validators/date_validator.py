from datetime import datetime

import fastapi
from loguru import logger


def date_validator(
    dates: tuple[datetime, datetime],
) -> tuple[datetime, datetime]:
    start_date = dates[0]
    end_date = dates[1]
    if start_date > end_date:
        logger.opt(lazy=True).debug(
            "{x}", x=lambda: f"{start_date=} is before {end_date=}"
        )
        raise fastapi.HTTPException(
            status_code=422,
            detail="Start date cannot be bigger than end date. "
            f"Invalid value: {start_date}",
        )
    if end_date > datetime.now():
        logger.opt(lazy=True).debug(
            "{x}",
            x=lambda: f"{end_date=} cannot be in future. "
            f"Now is {datetime.now()}",
        )
        raise fastapi.HTTPException(
            status_code=422,
            detail="End date cannot be in future. "
            f"Invalid value: {end_date}",
        )
    return start_date, end_date
