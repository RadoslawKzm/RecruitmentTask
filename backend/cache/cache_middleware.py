# Small rewrite of https://github.com/Sayanc2000/cache-fastapi

import hashlib
import json
from typing import List

from cache_fastapi.Backends.base_backend import BaseBackend
from fastapi import Request
from loguru import logger
from starlette.concurrency import iterate_in_threadpool
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response, StreamingResponse


class CacheMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, cached_endpoints: List[str], backend: BaseBackend):
        super().__init__(app)
        self.cached_endpoints = cached_endpoints
        self.backend = backend
        self.cache_age: int = 60

    def matches_any_path(self, path_url):
        for pattern in self.cached_endpoints:
            if pattern in path_url:
                return True
        return False

    @staticmethod
    def generate_hash(input_str: str) -> str:
        return hashlib.sha256(input_str.encode("utf-8")).hexdigest()

    @staticmethod
    async def get_request_body(request: Request) -> str:
        body_str = ""
        try:
            body_bytes = await request.body()
        except Exception as exc_info:  # noqa:841
            logger.opt(lazy=True).warning(
                "Error reading request body: {x}",
                x=lambda: exc_info,  # noqa:821
            )
            return body_str
        try:
            body_dict = await request.json()
            body_str = json.dumps(body_dict, sort_keys=True)
        except Exception:
            body_str = body_bytes.decode("utf-8")
        return body_str

    async def dispatch(self, request: Request, call_next) -> Response:
        path_url = request.url.path
        request_type = request.method
        # Only cache GET and PUT requests
        if request_type == "POST" or request_type == "DELETE":
            return await call_next(request)
        cache_control = request.headers.get("Cache-Control", "max-age=60")

        path_params_str: str = str(request.path_params)
        query_params_str: str = str(request.query_params)
        request_body = await self.get_request_body(request)
        combined_params = path_params_str + query_params_str + request_body

        # Generate a fixed-length hash for the body
        params_hash = self.generate_hash(combined_params)

        # Create a cache key that includes path, token, and hashed body
        key = f"{path_url}_{params_hash}"
        matches = self.matches_any_path(path_url)
        if not matches:
            return await call_next(request)
        if cache_control == "no-cache":
            return await call_next(request)

        # Check if response is cached
        cache_key = await self.backend.retrieve(key)
        if cache_key:
            # If the response is cached, return it directly
            json_data_str = cache_key[0]
            headers = {"Cache-Control": f"max-age:{cache_key[1]}"}
            return StreamingResponse(
                iter([json_data_str]),
                media_type="application/json",
                headers=headers,
            )

        # If not cached, proceed with the request
        response: Response = await call_next(request)
        response_body = [chunk async for chunk in response.body_iterator]
        response.body_iterator = iterate_in_threadpool(response_body)
        if not response_body:
            return response

        if cache_control == "no-store":
            # Skip caching for no-store
            return response

        if 300 > response.status_code >= 200:
            logger.debug("Creating cache of request")
            # Determine max-age
            max_age = self.cache_age
            if "max-age" in cache_control:
                max_age = int(cache_control.split("=")[1])
            # Cache the response
            await self.backend.create(
                response_body[0],
                key,
                max_age,
            )

        return response
