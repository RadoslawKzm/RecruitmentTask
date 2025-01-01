import functools

from loguru import logger

from backend.loguru_logger import log_config


def log_it(log_level="DEBUG"):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger.opt(lazy=True).log(
                log_level,
                f"Calling function '{func.__name__}' "
                f"with arguments: {args} and keyword arguments: {kwargs}",
            )
            try:
                # Log the function name and arguments at the specified log lvl

                # Call the actual function
                result = func(*args, **kwargs)

            except Exception as e:
                # Log the exception with traceback
                logger.opt(lazy=True).log(
                    log_config.unexpected_exception,
                    f"Exception occurred in function '{func.__name__}' "
                    f"with arguments: {args} and keyword arguments: {kwargs}",
                )
                raise e  # Re-raise the exception after logging it
            # Log the return value at the specified log level
            logger.opt(lazy=True).log(
                log_level,
                f"Function '{func.__name__}' returned: {result}",
            )

            return result

        return wrapper

    return decorator
