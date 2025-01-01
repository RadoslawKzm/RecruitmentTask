from gunicorn.glogging import Logger
from loguru import logger


class CustomLogger(Logger):
    def setup(self, cfg):
        super().setup(cfg)
        logger.add(
            "gunicorn_log.log",
            rotation="1 day",
            retention="10 days",
            level="INFO",
        )
