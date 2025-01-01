import uvicorn
from loguru import logger

if __name__ == "__main__":
    """
    Necessary for pycharm debugging purposes.
    If we run your module imported by another
        (including gunicorn) using something like:
    from manage import app then the value is 'app' or 'manage.app'
    """
    host: str = "0.0.0.0"
    port: int = 8765
    logger.info("App is loading!")
    logger.info("Started server process")
    logger.info("Waiting for application startup.")
    logger.info("Application startup complete.")
    logger.info(
        f"Uvicorn running on http://{host}:{port} (Press CTRL+C to quit)"
    )
    # uvicorn.run("main:app", host="0.0.0.0", port=8765, reload="true")
    uvicorn.run(
        "backend.api.app:app",
        host=host,
        port=port,
        # reload=True,
    )  # , log_level="critical")

# sudo lsof -i tcp:8765
# kill -15 (its soft) PID
# kill -9 (hardcore) PID
# lsof -i -P | grep :$PORT
