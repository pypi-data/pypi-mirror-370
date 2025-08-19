"""Web utilities."""

from __future__ import annotations

from contextlib import suppress

__all__: tuple[str, ...] = (
    "ErrorMiddleware",
    "RateLimitMiddleware",
)

import asyncio
from http import HTTPStatus
from typing import TYPE_CHECKING

from aiohttp import ClientResponseError
from loguru import logger
from pydantic import BaseModel, Field

from gongy.errors import (
    AccessDeniedError,
    GongError,
    MalformedRequestError,
    NotFoundError,
    RequestLimitExceededError,
    UnexpectedError,
)

if TYPE_CHECKING:  # pragma: no cover
    from aiohttp import ClientHandlerType, ClientRequest, ClientResponse

    from gongy.errors import GongErrorInfo


class ErrorMiddleware(BaseModel):
    """Middleware to handle errors."""

    errors: set[type[GongError]] = Field(
        default_factory=lambda: {
            MalformedRequestError,
            AccessDeniedError,
            NotFoundError,
            RequestLimitExceededError,
            UnexpectedError,
        }
    )

    async def __call__(
        self,
        req: ClientRequest,
        handler: ClientHandlerType,
    ) -> ClientResponse:
        """Handle errors."""
        try:
            resp = await handler(req)
            resp.raise_for_status()
        except ClientResponseError as e:
            for error_cls in self.errors:
                if error_cls.status == e.status:
                    info: GongErrorInfo = {}
                    with suppress(Exception):
                        info = await resp.json()
                    raise error_cls(
                        message=e.message,
                        request_id=info.get("requestId"),
                        errors=info.get("errors"),
                    ) from e
            raise
        return resp


class RateLimitMiddleware(BaseModel):
    """Middleware to handle rate limiting."""

    retries: int = Field(default=3, gt=0)
    default_delay: float = Field(default=1.0, gt=0)

    async def __call__(
        self,
        req: ClientRequest,
        handler: ClientHandlerType,
    ) -> ClientResponse:
        """Handle rate limiting.

        Raises for status after retries exhausted.
        """
        retries = self.retries
        while True:
            resp = await handler(req)
            if resp.status == HTTPStatus.TOO_MANY_REQUESTS:
                retry_after = float(resp.headers.get("Retry-After", self.default_delay))
                logger.warning(
                    "Rate limit exceeded for request: {method} {url}\n"
                    "Retrying after {retry_after}s ({retries} retries left)",
                    method=req.method,
                    url=req.url,
                    retry_after=retry_after,
                    retries=retries,
                )
                # Handle rate limit exceeded
                if retries <= 0:
                    return resp
                await asyncio.sleep(retry_after)  # Simple backoff strategy
                retries -= 1
                continue
            return resp
