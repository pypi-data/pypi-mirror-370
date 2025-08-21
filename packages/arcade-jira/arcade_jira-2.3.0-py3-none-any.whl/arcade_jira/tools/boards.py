import logging
from typing import Annotated, Any

from arcade_tdk import ToolContext, tool
from arcade_tdk.auth import Atlassian

from arcade_jira.client import APIType, JiraClient
from arcade_jira.tool_utils import boards_utils
from arcade_jira.utils import (
    add_pagination_to_response,
    clean_issue_dict,
    resolve_cloud_id,
    resolve_cloud_id_and_name,
)

logger = logging.getLogger(__name__)


@tool(
    requires_auth=Atlassian(
        scopes=[
            "read:board-scope:jira-software",  # /board/{boardId}, /board
            "read:project:jira",  # project info included in /board responses
            "read:issue-details:jira",  # issue metadata in /board/{boardId}, /board responses
            "read:jira-user",
        ]
    )
)
async def get_boards(
    context: ToolContext,
    board_identifiers_list: Annotated[
        list[str] | None,
        "List of board names or numeric IDs (as strings) to retrieve using pagination. "
        "Include all mentioned boards in a single list for best performance. "
        "Default None retrieves all boards. Maximum 50 boards returned per call.",
    ] = None,
    limit: Annotated[
        int,
        "Maximum number of boards to return (1-50). Defaults to max that is 50.",
    ] = 50,
    offset: Annotated[
        int,
        "Number of boards to skip for pagination. Must be 0 or greater. Defaults to 0.",
    ] = 0,
    atlassian_cloud_id: Annotated[
        str | None,
        "Atlassian Cloud ID to use. Defaults to None (uses single authorized cloud).",
    ] = None,
) -> Annotated[
    dict[str, Any],
    "Dictionary with 'boards' list containing board metadata (ID, name, type, location) "
    "and 'errors' array for not found boards. Includes pagination metadata and deduplication.",
]:
    """
    Retrieve Jira boards either by specifying their names or IDs, or get all
    available boards.
    All requests support offset and limit with a maximum of 50 boards returned per call.

    MANDATORY ACTION: ALWAYS when you need to get multiple boards, you must
    include all the board identifiers in a single call rather than making
    multiple separate tool calls, as this provides much better performance, not doing that will
    bring huge performance penalties.

    The tool automatically handles mixed identifier types (names and IDs), deduplicates results, and
    falls back from ID lookup to name lookup when needed.
    """
    cloud_data = await resolve_cloud_id_and_name(context, atlassian_cloud_id)
    client = JiraClient(context, cloud_data["cloud_id"], client_type=APIType.AGILE)
    limit = boards_utils.validate_board_limit(limit)

    # If no specific boards requested, get all boards with pagination
    if not board_identifiers_list:
        return await boards_utils.get_boards_with_offset(
            client, limit, offset, cloud_data["cloud_name"]
        )

    # Process specific board identifiers with deduplication
    return await boards_utils.get_boards_by_identifiers(
        client, board_identifiers_list, cloud_data["cloud_name"], limit, offset
    )


@tool(
    requires_auth=Atlassian(
        scopes=[
            "read:board-scope:jira-software",  # /board/{boardId}/backlog
            "read:issue-details:jira",  # issue details in backlog responses
        ]
    )
)
async def get_board_backlog_issues(
    context: ToolContext,
    board_id: Annotated[
        str,
        "The ID of the board to retrieve backlog issues from. Must be a valid board ID "
        "that supports backlogs (typically Scrum or Kanban boards).",
    ],
    limit: Annotated[
        int,
        "The maximum number of issues to return. Must be between 1 and 100 inclusive. "
        "Controls pagination and determines how many issues are fetched and returned. "
        "Defaults to 50 for improved performance.",
    ] = 50,
    offset: Annotated[
        int,
        "The number of issues to skip before starting to return results. "
        "Used for pagination when the backlog has many issues. "
        "For example, offset=50 with limit=50 would return issues 51-100. "
        "Must be 0 or greater. Defaults to 0.",
    ] = 0,
    atlassian_cloud_id: Annotated[
        str | None,
        "The ID of the Atlassian Cloud to use (defaults to None). If not provided and the user has "
        "a single cloud authorized, the tool will use that. Otherwise, an error will be raised.",
    ] = None,
) -> Annotated[
    dict[str, Any],
    "A dictionary containing the board information, list of backlog issues, and pagination "
    "metadata. Issues are returned with full details including summary, status, assignee, "
    "and other fields. If the board doesn't support backlogs or doesn't exist, appropriate "
    "error information is returned.",
]:
    """
    Get all issues in a board's backlog with pagination support.
    Returns issues that are not currently assigned to any active sprint.

    The backlog contains issues that are ready to be planned into future sprints.
    Only boards that support backlogs (like Scrum and Kanban boards) will return results.
    """
    atlassian_cloud_id = await resolve_cloud_id(context, atlassian_cloud_id)
    client = JiraClient(context, atlassian_cloud_id, client_type=APIType.AGILE)
    limit = boards_utils.validate_board_limit(limit)

    try:
        response = await client.get(
            f"/board/{board_id}/backlog",
            params={
                "startAt": offset,
                "maxResults": limit,
                "expand": "renderedFields",
            },
        )

        issues = [clean_issue_dict(issue) for issue in response.get("issues", [])]

        result = {
            "issues": issues,
            "isLast": response.get("isLast", False),
            "total": response.get("total"),
        }

        return add_pagination_to_response(result, issues, limit, offset, response.get("total"))

    except Exception as e:
        error_message = f"Failed to retrieve backlog issues for board '{board_id}': {e!s}"
        return {
            "error": error_message,
            "board_id": board_id,
        }
