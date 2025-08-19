"""Gong MCP."""

__all__: tuple[str, ...] = ()

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime

from gongy import Gongy
from gongy.models import (
    CallID,
    CallResponse,
    CallsExpandedResponse,
    CallsResponse,
    CallTranscriptsResponse,
    ContentSelector,
    UserID,
    WorkspaceID,
)
from mcp.server.fastmcp import Context, FastMCP
from mcp.server.session import ServerSession

from gong_mcp.settings import Settings


@dataclass
class AppContext:
    """Application context with typed dependencies."""

    gongy: Gongy


@asynccontextmanager
async def app_lifespan(_server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage application lifecycle with type-safe context."""
    # Initialize on startup
    settings = Settings()
    async with Gongy(
        api_key=settings.gong_api_key,
        secret=settings.gong_api_secret,
    ) as gongy:
        yield AppContext(gongy=gongy)


# Pass lifespan to server
mcp = FastMCP(name="Gong", lifespan=app_lifespan)


@mcp.tool()
async def get_calls(
    *,
    start: datetime,
    end: datetime,
    workspace: WorkspaceID | None = None,
    ctx: Context[ServerSession, AppContext],
) -> list[CallsResponse]:
    """Get Gong calls."""
    gongy = ctx.request_context.lifespan_context.gongy
    return [
        call
        async for call in gongy.get_calls(
            start=start,
            end=end,
            workspace=workspace,
        )
    ]


@mcp.tool()
async def get_call(
    *,
    call_id: str,
    ctx: Context[ServerSession, AppContext],
) -> CallResponse:
    """Get a specific Gong call."""
    gongy = ctx.request_context.lifespan_context.gongy
    return await gongy.get_call(id=call_id)


@mcp.tool()
async def get_calls_extensive(  # noqa: PLR0913
    *,
    start: datetime | None = None,
    end: datetime | None = None,
    workspace: WorkspaceID | None = None,
    call_ids: list[CallID] | None = None,
    primary_user_ids: list[UserID] | None = None,
    content_selector: ContentSelector | None = None,
    ctx: Context[ServerSession, AppContext],
) -> list[CallsExpandedResponse]:
    """Get extensive Gong calls."""
    gongy = ctx.request_context.lifespan_context.gongy
    return [
        call
        async for call in gongy.get_calls_extensive(
            start=start,
            end=end,
            workspace=workspace,
            ids=call_ids,
            primary_user_ids=primary_user_ids,
            content_selector=content_selector,
        )
    ]


@mcp.tool()
async def get_call_transcripts(
    *,
    start: datetime | None = None,
    end: datetime | None = None,
    workspace: WorkspaceID | None = None,
    call_ids: list[CallID] | None = None,
    ctx: Context[ServerSession, AppContext],
) -> list[CallTranscriptsResponse]:
    """Get extensive Gong calls."""
    gongy = ctx.request_context.lifespan_context.gongy
    return [
        call
        async for call in gongy.get_call_transcripts(
            start=start,
            end=end,
            workspace=workspace,
            ids=call_ids,
        )
    ]
