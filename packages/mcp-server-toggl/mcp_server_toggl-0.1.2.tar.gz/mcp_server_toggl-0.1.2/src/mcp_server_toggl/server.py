import os
import base64
import json
from typing import Annotated, Optional, List

import httpx
from fastmcp import FastMCP
from pydantic import Field


TOGGL_API_URL = "https://api.track.toggl.com/api/v9"


mcp = FastMCP(
    name="Toggl MCP Server",
    instructions="A Model Context Protocol server that provides tools to fetch and manage Toggl Track data.",
)


def _get_api_token() -> str:
    """Fetch the Toggl API token from environment variables.

    Prefers `TOGGL_API_TOKEN` to match official docs, falls back to `TOGGL_API_KEY`.
    """
    token = os.getenv("TOGGL_API_TOKEN") or os.getenv("TOGGL_API_KEY")
    if not token:
        raise ValueError(
            "Environment variable TOGGL_API_TOKEN (or TOGGL_API_KEY) is not set"
        )
    return token


def _get_auth_header_with_token(token: str) -> str:
    credentials = f"{token}:api_token".encode("utf-8")
    encoded = base64.b64encode(credentials).decode("utf-8")
    return f"Basic {encoded}"


async def _execute_api_request(
    url: str, method: str, body: Optional[dict] = None
) -> object:
    """Execute an HTTP request to the Toggl API and return parsed JSON or a success message for DELETE.

    Raises a descriptive exception on non-2xx responses.
    """
    token = _get_api_token()
    headers = {
        "Content-Type": "application/json",
        "Authorization": _get_auth_header_with_token(token),
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.request(
            method=method,
            url=url,
            headers=headers,
            content=(json.dumps(body) if body is not None else None),
        )
        if response.is_success:
            if method.upper() == "DELETE":
                return {"message": "Deleted successfully"}
            return response.json()
        else:
            response.raise_for_status()


def _format_response(data: object) -> str:
    """Pretty-print JSON for MCP textual output."""
    return json.dumps(data, ensure_ascii=False, indent=2)


def _is_valid_iso_datetime(value: str) -> bool:
    # Basic validation: ISO 8601 with 'T' separator and parseable by fromisoformat (after trimming Z)
    if "T" not in value:
        return False
    # Allow trailing Z by replacing with +00:00 for Python parsing
    try:
        from datetime import datetime

        candidate = value.replace("Z", "+00:00")
        datetime.fromisoformat(candidate)
        return True
    except Exception:
        return False


@mcp.tool(
    description="Get time entries for the current user with optional filters",
)
async def get_time_entries(
    startDate: Annotated[
        Optional[str],
        Field(description="Start datetime (ISO 8601, e.g., 2024-04-08T00:00:00Z)"),
    ] = None,
    endDate: Annotated[
        Optional[str],
        Field(description="End datetime (ISO 8601, e.g., 2024-04-14T23:59:59Z)"),
    ] = None,
    before: Annotated[
        Optional[str],
        Field(description="Return entries before this datetime (ISO 8601)"),
    ] = None,
    since: Annotated[
        Optional[int],
        Field(description="Return entries changed since this UNIX timestamp"),
    ] = None,
) -> str:
    if startDate and not _is_valid_iso_datetime(startDate):
        raise ValueError("startDate is not a valid ISO 8601 datetime")
    if endDate and not _is_valid_iso_datetime(endDate):
        raise ValueError("endDate is not a valid ISO 8601 datetime")
    if before and not _is_valid_iso_datetime(before):
        raise ValueError("before is not a valid ISO 8601 datetime")

    params: list[tuple[str, str]] = []
    if startDate:
        params.append(("start_date", startDate))
    if endDate:
        params.append(("end_date", endDate))
    if before:
        params.append(("before", before))
    if since is not None:
        params.append(("since", str(since)))

    query = f"?{httpx.QueryParams(params)}" if params else ""
    url = f"{TOGGL_API_URL}/me/time_entries{query}"
    data = await _execute_api_request(url, "GET")
    return _format_response(data)


@mcp.tool(description="Get the currently running time entry for the authenticated user")
async def get_current_time_entry() -> str:
    url = f"{TOGGL_API_URL}/me/time_entries/current"
    data = await _execute_api_request(url, "GET")
    return _format_response(data)


@mcp.tool(description="Create a new time entry in a workspace")
async def create_time_entry(
    workspaceId: Annotated[int, Field(description="Workspace ID")],
    start: Annotated[str, Field(description="Start time (ISO 8601)")],
    description: Annotated[
        Optional[str], Field(description="Description of the time entry")
    ] = None,
    projectId: Annotated[Optional[int], Field(description="Project ID")] = None,
    billable: Annotated[
        Optional[bool],
        Field(description="Whether the time entry is billable", default=True),
    ] = True,
    duration: Annotated[
        Optional[int], Field(description="Duration in seconds (omit for running entry)")
    ] = None,
    tags: Annotated[
        Optional[List[str]], Field(description="Name of tags to assign")
    ] = None,
) -> str:
    if not _is_valid_iso_datetime(start):
        raise ValueError("start is not a valid ISO 8601 datetime")
    url = f"{TOGGL_API_URL}/workspaces/{workspaceId}/time_entries"
    body = {
        "description": description,
        "project_id": projectId,
        "billable": billable,
        "start": start,
        "duration": duration,
        "tags": tags,
        "created_with": "mcp-server-toggl",
        "workspace_id": workspaceId,
    }
    # Remove None values to avoid overriding server defaults
    body = {k: v for k, v in body.items() if v is not None}
    data = await _execute_api_request(url, "POST", body=body)
    return _format_response(data)


@mcp.tool(description="Update a single time entry")
async def update_time_entry(
    workspaceId: Annotated[int, Field(description="Workspace ID")],
    timeEntryId: Annotated[int, Field(description="Time entry ID")],
    description: Annotated[Optional[str], Field(description="Description")] = None,
    projectId: Annotated[Optional[int], Field(description="Project ID")] = None,
    taskId: Annotated[Optional[int], Field(description="Task ID")] = None,
    billable: Annotated[Optional[bool], Field(description="Billable flag")] = None,
    start: Annotated[Optional[str], Field(description="Start time (ISO 8601)")] = None,
    duration: Annotated[Optional[int], Field(description="Duration in seconds")] = None,
    tags: Annotated[Optional[List[str]], Field(description="Tags to set")] = None,
) -> str:
    if start is not None and not _is_valid_iso_datetime(start):
        raise ValueError("start is not a valid ISO 8601 datetime")
    url = f"{TOGGL_API_URL}/workspaces/{workspaceId}/time_entries/{timeEntryId}"
    body = {
        "description": description,
        "project_id": projectId,
        "task_id": taskId,
        "billable": billable,
        "start": start,
        "duration": duration,
        "tags": tags,
        "created_with": "mcp-server-toggl",
        "workspace_id": workspaceId,
    }
    body = {k: v for k, v in body.items() if v is not None}
    data = await _execute_api_request(url, "PUT", body=body)
    return _format_response(data)


@mcp.tool(description="Delete a time entry")
async def delete_time_entry(
    workspaceId: Annotated[int, Field(description="Workspace ID")],
    timeEntryId: Annotated[int, Field(description="Time entry ID")],
) -> str:
    url = f"{TOGGL_API_URL}/workspaces/{workspaceId}/time_entries/{timeEntryId}"
    data = await _execute_api_request(url, "DELETE")
    return _format_response(data)


@mcp.tool(description="Stop a running time entry")
async def stop_time_entry(
    workspaceId: Annotated[int, Field(description="Workspace ID")],
    timeEntryId: Annotated[int, Field(description="Time entry ID")],
) -> str:
    url = f"{TOGGL_API_URL}/workspaces/{workspaceId}/time_entries/{timeEntryId}/stop"
    data = await _execute_api_request(url, "PATCH")
    return _format_response(data)


@mcp.tool(description="List workspaces accessible to the authenticated user")
async def get_workspaces() -> str:
    url = f"{TOGGL_API_URL}/workspaces"
    data = await _execute_api_request(url, "GET")
    return _format_response(data)


@mcp.tool(description="Get tags for a workspace")
async def get_workspace_tags(
    workspaceId: Annotated[int, Field(description="Workspace ID")],
    page: Annotated[
        Optional[int], Field(description="Page number for pagination", ge=1, default=1)
    ] = 1,
    perPage: Annotated[
        Optional[int],
        Field(description="Items per page", ge=1, default=20, le=50),
    ] = 20,
) -> str:
    params: list[tuple[str, str]] = []
    if page is not None:
        params.append(("page", str(page)))
    if perPage is not None:
        params.append(("per_page", str(perPage)))
    query = f"?{httpx.QueryParams(params)}" if params else ""
    url = f"{TOGGL_API_URL}/workspaces/{workspaceId}/tags{query}"
    data = await _execute_api_request(url, "GET")
    return _format_response(data)


@mcp.tool(description="Get clients for a workspace")
async def get_workspace_clients(
    workspaceId: Annotated[int, Field(description="Workspace ID")],
    page: Annotated[
        Optional[int], Field(description="Page number for pagination", ge=1, default=1)
    ] = 1,
    perPage: Annotated[
        Optional[int],
        Field(description="Items per page", ge=1, default=20, le=50),
    ] = 20,
) -> str:
    params: list[tuple[str, str]] = []
    if page is not None:
        params.append(("page", str(page)))
    if perPage is not None:
        params.append(("per_page", str(perPage)))
    query = f"?{httpx.QueryParams(params)}" if params else ""
    url = f"{TOGGL_API_URL}/workspaces/{workspaceId}/clients{query}"
    data = await _execute_api_request(url, "GET")
    return _format_response(data)


@mcp.tool(description="List projects in a workspace with optional filters")
async def get_workspace_projects(
    workspaceId: Annotated[int, Field(description="Workspace ID")],
    active: Annotated[
        Optional[bool], Field(description="Only include active projects", default=True)
    ] = True,
    page: Annotated[
        Optional[int], Field(description="Page number for pagination", ge=1, default=1)
    ] = 1,
    perPage: Annotated[
        Optional[int],
        Field(description="Items per page", ge=1, default=20, le=50),
    ] = 20,
) -> str:
    params: list[tuple[str, str]] = []
    if active is not None:
        params.append(("active", str(active).lower()))
    if page is not None:
        params.append(("page", str(page)))
    if perPage is not None:
        params.append(("per_page", str(perPage)))
    query = f"?{httpx.QueryParams(params)}" if params else ""
    url = f"{TOGGL_API_URL}/workspaces/{workspaceId}/projects{query}"
    data = await _execute_api_request(url, "GET")
    return _format_response(data)


def main() -> None:
    """Run the Toggl MCP server."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
