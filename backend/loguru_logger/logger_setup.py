import sys

from asgi_correlation_id import correlation_id
from loguru import logger

from backend.loguru_logger import log_config

# log_level: str = "INFO"
log_level: str = "DEBUG"


def correlation_id_filter(record):
    record["correlation_id"] = correlation_id.get()
    return record["correlation_id"] or "No correlation_id"
    # corr_id = correlation_id.get() or "No correlation_id"
    # record["correlation_id"] = corr_id
    # return corr_id


def logger_setup():
    logger.remove()
    fmt = (
        "<level>{level: <8}</level>"
        " | <black>{correlation_id}</black>"
        " | <green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>"
        " | <cyan>{name}</cyan>:<cyan>{function}</cyan>"
        ":<cyan>{line}</cyan> - <level>{message}</level>"
    )
    logger.add(
        sys.stderr,
        format=fmt,
        level=log_level,
        filter=correlation_id_filter,
        enqueue=True,
        diagnose=True,
        backtrace=False,
    )
    logger.add(
        "logs/loguru.log",
        rotation="1 hour",
        retention="1 day",
        format=fmt,
        level=log_level,
        filter=correlation_id_filter,
        enqueue=True,
        backtrace=False,
        diagnose=True,
    )
    logger.level(
        log_config.request_validation_exception, no=11, color="<black>"
    )
    logger.level(log_config.http_exception, no=31, color="<yellow>")
    logger.level(log_config.handled_internal_exception, no=41, color="<red>")
    logger.level(
        log_config.unexpected_exception, no=51, color="<red><bold><underline>"
    )


# flake8: noqa: E501
# logger.add("logs/loguru.log", rotation="5 seconds", retention="1 day")
# logger.add("logs/loguru.log", enqueue=True)

# TRACE (5): used to record fine-grained information about the program's execution path for diagnostic purposes.
# DEBUG (10): used by developers to record messages for debugging purposes.
# INFO (20): used to record informational messages that describe the normal operation of the program.
# SUCCESS (25): similar to INFO but used to indicate the success of an operation.
# WARNING (30): used to indicate an unusual event that may require further investigation.
# ERROR (40): used to record error conditions that affected a specific operation.
# CRITICAL (50): used to record error conditions that prevent a core function from working.
# flake8: noqa: enable
