"""Gong API."""

from __future__ import annotations

__all__: tuple[str, ...] = ("Gongy",)

from typing import TYPE_CHECKING

from aiohttp import BasicAuth, ClientSession
from pydantic import BaseModel, ConfigDict, Field
from yarl import URL

from gongy.models import (
    CallID,
    CallResponse,
    CallsExpandedResponse,
    CallsRequest,
    CallsResponse,
    CallTranscriptsResponse,
    ContentSelector,
    FilterParams,
    UserID,
)
from gongy.utils.web import (
    ErrorMiddleware,
    RateLimitMiddleware,
)

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import AsyncGenerator
    from datetime import datetime
    from types import TracebackType
    from typing import Self

    from gongy.models import Cursor, WorkspaceID


class Gongy(BaseModel):
    """Gong API client."""

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )

    api_key: str
    secret: str

    retries: int = Field(default=3, gt=0)
    delay: float = Field(default=1.0, gt=0)

    base_url: URL = URL("https://api.gong.io")

    raw_session: ClientSession | None = Field(default=None, init=False)

    @property
    def session(self) -> ClientSession:
        """Get the aiohttp session."""
        if self.raw_session is None:
            msg = (
                f"Session not initialized. "
                f"Use 'async with {self.__class__.__name__}(...) as gongy:'"
            )
            raise RuntimeError(msg)
        return self.raw_session

    async def __aenter__(self) -> Self:
        """Enter the async context."""
        self.raw_session = ClientSession(
            auth=BasicAuth(
                login=self.api_key,
                password=self.secret,
            ),
            middlewares=(
                ErrorMiddleware(),
                RateLimitMiddleware(retries=self.retries, default_delay=self.delay),
            ),
        )
        await self.session.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit the async context."""
        await self.session.__aexit__(exc_type, exc_val, exc_tb)
        self.raw_session = None

    @property
    def v2(self) -> URL:
        """Get the v2 API URL."""
        return self.base_url / "v2"

    async def get_calls_page(
        self,
        start: datetime,
        end: datetime,
        workspace: WorkspaceID | None = None,
        cursor: Cursor | None = None,
    ) -> CallsResponse:
        """Get a single page of calls from the Gong API."""
        url = self.v2 / "calls"
        params = {
            "fromDateTime": start.isoformat(),
            "toDateTime": end.isoformat(),
        }
        if workspace is not None:
            params["workspaceId"] = workspace
        if cursor is not None:
            params["cursor"] = cursor
        async with self.session.get(url, params=params) as response:
            data = await response.json()
            return CallsResponse.model_validate(data)

    async def get_calls(
        self,
        start: datetime,
        end: datetime,
        workspace: WorkspaceID | None = None,
    ) -> AsyncGenerator[CallsResponse]:
        """Get calls from the Gong API in batches."""
        cursor: Cursor | None = None
        while True:
            response = await self.get_calls_page(
                start=start,
                end=end,
                workspace=workspace,
                cursor=cursor,
            )
            yield response
            cursor = response.records.cursor
            if cursor is None:
                break

    async def get_call(
        self,
        id: CallID,
    ) -> CallResponse:
        """Get a single call from the Gong API."""
        url = self.v2 / "calls" / id
        async with self.session.get(url) as response:
            data = await response.json()
            return CallResponse.model_validate(data)

    async def get_calls_extensive_page(  # noqa: PLR0913
        self,
        start: datetime | None = None,
        end: datetime | None = None,
        workspace: WorkspaceID | None = None,
        ids: list[CallID] | None = None,
        primary_user_ids: list[UserID] | None = None,
        content_selector: ContentSelector | None = None,
        cursor: Cursor | None = None,
    ) -> CallsExpandedResponse:
        """Get a single page of extensive calls from the Gong API."""
        url = self.v2 / "calls" / "extensive"
        calls_request = CallsRequest(
            cursor=cursor,
            filter=FilterParams(
                from_date_time=start,
                to_date_time=end,
                workspace_id=workspace,
                call_ids=ids,
                primary_user_ids=primary_user_ids,
            ),
            content_selector=content_selector,
        )
        async with self.session.post(
            url,
            json=calls_request.model_dump(
                by_alias=True,
                exclude_none=True,
                mode="json",
            ),
        ) as response:
            data = await response.json()
            return CallsExpandedResponse.model_validate(data)

    async def get_calls_extensive(  # noqa: PLR0913
        self,
        start: datetime | None = None,
        end: datetime | None = None,
        workspace: WorkspaceID | None = None,
        ids: list[CallID] | None = None,
        primary_user_ids: list[UserID] | None = None,
        content_selector: ContentSelector | None = None,
    ) -> AsyncGenerator[CallsExpandedResponse]:
        """Get extensive calls from the Gong API in batches."""
        cursor: Cursor | None = None
        while True:
            response = await self.get_calls_extensive_page(
                start=start,
                end=end,
                workspace=workspace,
                ids=ids,
                primary_user_ids=primary_user_ids,
                content_selector=content_selector,
                cursor=cursor,
            )
            yield response
            cursor = response.records.cursor
            if cursor is None:
                break

    async def get_call_transcripts_page(
        self,
        start: datetime | None = None,
        end: datetime | None = None,
        workspace: WorkspaceID | None = None,
        ids: list[CallID] | None = None,
        cursor: Cursor | None = None,
    ) -> CallTranscriptsResponse:
        """Get a single page of call transcripts from the Gong API."""
        url = self.v2 / "calls" / "transcript"
        calls_request = CallsRequest(
            cursor=cursor,
            filter=FilterParams(
                from_date_time=start,
                to_date_time=end,
                workspace_id=workspace,
                call_ids=ids,
            ),
        )
        async with self.session.post(
            url,
            json=calls_request.model_dump(
                by_alias=True,
                exclude_none=True,
                mode="json",
            ),
        ) as response:
            data = await response.json()
            return CallTranscriptsResponse.model_validate(data)

    async def get_call_transcripts(
        self,
        start: datetime | None = None,
        end: datetime | None = None,
        workspace: WorkspaceID | None = None,
        ids: list[CallID] | None = None,
    ) -> AsyncGenerator[CallTranscriptsResponse]:
        """Get call transcripts from the Gong API in batches."""
        cursor: Cursor | None = None
        while True:
            response = await self.get_call_transcripts_page(
                start=start,
                end=end,
                workspace=workspace,
                ids=ids,
                cursor=cursor,
            )
            yield response
            cursor = response.records.cursor
            if cursor is None:
                break
