import typing
import uuid
from contextlib import asynccontextmanager

from asgi_correlation_id import CorrelationIdMiddleware
from asgi_correlation_id.middleware import is_valid_uuid4
from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from starlette import status
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse

from backend.api.routers import (
    about_router,
    healthcheck_router,
    project_router,
    projects_router,
)
from backend.cache.cache_middleware import CacheMiddleware
from backend.cache.memory_backend import MemoryBackend
from backend.database.postgres.session import DbContext, init_db
from backend.loguru_logger.logger_setup import log_config, logger_setup


@asynccontextmanager
async def lifespan(func_app: FastAPI) -> typing.AsyncContextManager[None]:
    logger_setup()
    # await init_db(_engine=engine)
    init_db()
    db_context = DbContext()
    yield
    if db_context.engine is not None:
        # Close the DB connection
        await db_context.close()


_app = FastAPI(lifespan=lifespan, root_path="/api")


_app.include_router(router=about_router)
_app.include_router(router=healthcheck_router)
_app.include_router(router=project_router)
_app.include_router(router=projects_router)


origins = [
    # "0.0.0.0",
    # "http://localhost",
    # "https://localhost",
    "*"
]
_app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["X-Requested-With", "X-Request-ID"],
    expose_headers=["X-Request-ID"],
)

cached_endpoints = ["/project", "/projects"]
backend = MemoryBackend()
_app.add_middleware(
    CacheMiddleware,
    cached_endpoints=cached_endpoints,
    backend=backend,
)


@_app.middleware("http")
async def log_user_metadata(
    request: Request, call_next: typing.Any
) -> typing.Any:
    client_ip: str = request.client.host
    client_port: int = request.client.port
    # client_language = request.headers["accept-language"]
    logger.info(f"{request.method} {request.url.path}")
    logger.debug(f"IP={client_ip}, Port={client_port}")
    return await call_next(request)


@_app.middleware("http")
async def exception_logger(
    request: Request, call_next: typing.Any
) -> typing.Any:
    response = await call_next(request)
    log_msg: str = (
        f"{request.method} {request.url.path} {response.status_code}"
    )
    metadata_str = log_msg
    logger.opt(lazy=True).info(log_msg)
    if response.status_code < 400:
        # Less than 400
        logger.opt(lazy=True).debug(metadata_str)
    elif response.status_code == 422:
        # 422
        logger.opt(lazy=True).log(
            log_config.request_validation_exception, metadata_str
        )
    elif 400 <= response.status_code < 500:
        # 400-499
        logger.opt(lazy=True).log(log_config.http_exception, metadata_str)
    elif response.status_code == 501:
        # 501
        logger.opt(lazy=True).exception(
            log_config.unexpected_exception, metadata_str
        )
    else:
        # Rest of 500
        logger.opt(lazy=True).exception(
            log_config.handled_internal_exception,
            metadata_str,
        )
    return response


def init_listeners(func_app: FastAPI) -> FastAPI:
    """Function to add listeners to FASTAPI app"""
    logger.info("Initializing global exception handlers.")

    @func_app.exception_handler(HTTPException)
    async def custom_http_exception_handler(
        request: Request,
        exc: HTTPException,
    ) -> Response:
        """Exception handler for HTTPException"""
        headers = getattr(exc, "headers", None)
        logger.opt(lazy=True).log(
            log_config.http_exception,
            "Traceback: {traceback}, Request: {request}, Headers: {headers}",
            traceback=lambda: f"{exc}",
            request=lambda: f"{request}",
            headers=lambda: f"{headers}",
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": f"{exc.detail}"},
            headers=headers,
        )

    @func_app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> Response:
        """Exception handler for RequestValidationError"""
        headers = getattr(exc, "headers", None)
        msg = {"detail": "Request validation failed"}
        msg.update(exc.args[0][0])
        logger.opt(lazy=True).log(
            log_config.request_validation_exception,
            "Traceback: {traceback}, Request: {request}, Headers: {headers}",
            traceback=lambda: f"{exc}",
            request=lambda: f"{request}",
            headers=lambda: f"{headers}",
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=msg,
            headers=headers,
        )

    @func_app.exception_handler(Exception)
    async def custom_generic_exception_handler(
        request: Request,
        exc: Exception,
    ) -> Response:
        """Exception handler for generic exceptions
        Hijacking detail and other vulnerable data from end-user.
        Minimizing security risk through minimizing exposition.
        """
        headers = getattr(exc, "headers", None)
        logger.opt(lazy=True).log(
            log_config.request_validation_exception,
            "Traceback: {traceback}, Request: {request}, Headers: {headers}",
            traceback=lambda: f"{exc}",
            request=lambda: f"{request}",
            headers=lambda: f"{headers}",
        )
        return JSONResponse(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            content={
                "detail": "Internal Server Error. "
                "Our team is already working on it."
            },
            headers=headers,
        )

    return func_app


_app = init_listeners(_app)

_app.add_middleware(
    CorrelationIdMiddleware,
    header_name="X-Request-ID",
    update_request_header=True,
    generator=lambda: uuid.uuid4().hex,
    validator=is_valid_uuid4,
    transformer=lambda a: a,
)


app: FastAPI = _app


# # sudo lsof -i tcp:8080
# # kill -15 (its soft) PID
# # kill -9 (hardcore) PID
