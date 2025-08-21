import asyncio
import logging
from typing import Annotated, Any

from arcade_tdk import ToolContext, tool
from arcade_tdk.auth import Atlassian
from arcade_tdk.errors import ToolExecutionError

from arcade_jira.client import APIType, JiraClient
from arcade_jira.constants import SprintState
from arcade_jira.tool_utils import boards_utils, sprint_planning_utils
from arcade_jira.tools.boards import get_boards
from arcade_jira.utils import (
    add_pagination_to_response,
    resolve_cloud_id,
    resolve_cloud_id_and_name,
)

logger = logging.getLogger(__name__)

# Error message constants
SPRINT_ID_REQUIRED_ERROR = "Sprint ID is required. Please provide a valid sprint ID."
ISSUE_IDS_REQUIRED_ERROR = (
    "Issue IDs are required. Please provide a non-empty list of issue IDs to add to the sprint."
)
ISSUE_LIMIT_ERROR = (
    "Cannot process more than 50 issues in one operation. "
    "Please split your request into smaller batches."
)
BOARD_LIMIT_ERROR = (
    "Cannot process more than 25 boards in one operation. "
    "Please split your request into smaller batches."
)
MISSING_ISSUE_IDENTIFIERS_ERROR = "At least one issue identifier must be provided"


@tool(
    requires_auth=Atlassian(
        scopes=[
            "read:board-scope:jira-software",  # /board, /board/{boardId} (via get_boards)
            "read:project:jira",  # project info from /board responses (via get_boards)
            "read:sprint:jira-software",  # /board/{boardId}/sprint
            "read:issue-details:jira",  # issue metadata in /board/{boardId}, /board responses
            # administrative access to /board/{boardId}/sprint
            "read:board-scope.admin:jira-software",
            "read:jira-user",
        ]
    )
)
async def list_sprints_for_boards(
    context: ToolContext,
    board_identifiers_list: Annotated[
        list[str] | None,
        "List of board names or numeric IDs (as strings) to retrieve sprints from. "
        "Include all mentioned boards in a single list for best performance. "
        "Maximum 25 boards per operation. Optional, defaults to None.",
    ] = None,
    max_sprints_per_board: Annotated[
        int,
        "Maximum sprints per board (1-50). Latest sprints first. Optional, defaults to 50.",
    ] = 50,
    offset: Annotated[
        int,
        "Number of sprints to skip per board for pagination. Optional, defaults to 0.",
    ] = 0,
    state: Annotated[
        SprintState | None,
        "Filter by sprint state. NOTE: Date filters (start_date, end_date, specific_date) "
        "have higher priority than state filtering. Use state filtering only when no date "
        "criteria is specified. For temporal queries like 'last month' or 'next week', "
        "use date parameters instead. Optional, defaults to None (all states).",
    ] = None,
    start_date: Annotated[
        str | None,
        "Start date filter in YYYY-MM-DD format. Can combine with end_date. "
        "Optional, defaults to None.",
    ] = None,
    end_date: Annotated[
        str | None,
        "End date filter in YYYY-MM-DD format. Can combine with start_date. "
        "Optional, defaults to None.",
    ] = None,
    specific_date: Annotated[
        str | None,
        "Specific date in YYYY-MM-DD to find sprints active on that date. "
        "Cannot combine with start_date/end_date. Optional, defaults to None.",
    ] = None,
    atlassian_cloud_id: Annotated[
        str | None,
        "Atlassian Cloud ID to use. Optional, defaults to None (uses single authorized cloud).",
    ] = None,
) -> Annotated[
    dict[str, Any],
    "Dict with 'boards' list, 'sprints_by_board' mapping, and 'errors' array. "
    "Sprints sorted latest first.",
]:
    """
    Retrieve sprints from Jira boards with filtering options for planning and tracking purposes.

    Use this when you need to view sprints from specific boards or find sprints within specific
    date ranges. For temporal queries like "last month", "next week", or "this quarter",
    prioritize date parameters over state filtering. Leave board_identifiers_list as None
    to get sprints from all available boards.

    DATE FILTERING PRIORITY: When users request sprints by time periods (e.g., "last month",
    "next week"), use date parameters (start_date, end_date, specific_date) rather than
    state filtering, as temporal criteria take precedence over sprint status.

    Returns sprint data along with a backlog GUI URL link where you can see detailed sprint
    information and manage sprint items.

    MANDATORY ACTION: ALWAYS when you need to get sprints from multiple boards, you must
    include all the board identifiers in a single call rather than making
    multiple separate tool calls, as this provides much better performance, not doing that will
    bring huge performance penalties.

    BOARD LIMIT: Maximum of 25 boards can be processed in a single operation. If you need to
    process more boards, split the request into multiple batches of 25 or fewer boards each.

    Handles mixed board identifiers (names and IDs) with automatic fallback and deduplication.
    All boards are processed concurrently for optimal performance.
    """
    api_states = state.to_api_value() if state else None

    sprint_planning_utils.validate_parameters(specific_date, start_date, end_date, api_states)

    max_sprints_per_board = sprint_planning_utils.validate_sprint_limit(max_sprints_per_board)
    cloud_data = await resolve_cloud_id_and_name(context, atlassian_cloud_id)
    client = JiraClient(context, cloud_data["cloud_id"], client_type=APIType.AGILE)

    results: dict[str, Any] = {
        "boards": [],
        "sprints_by_board": {},
        "errors": [],
    }

    board_response = await get_boards(
        context, board_identifiers_list, atlassian_cloud_id=cloud_data["cloud_id"]
    )

    boards_to_process = sprint_planning_utils.determine_boards_to_process(
        board_identifiers_list, board_response
    )

    if len(boards_to_process) > 25:
        error_msg = f"{BOARD_LIMIT_ERROR} You provided {len(boards_to_process)} boards."
        raise ToolExecutionError(error_msg)

    board_tasks = [
        sprint_planning_utils.process_single_board(
            context,
            client,
            board_id,
            board_response,
            offset,
            max_sprints_per_board,
            api_states,
            start_date,
            end_date,
            specific_date,
            cloud_data["cloud_name"],
        )
        for board_id in boards_to_process
    ]

    board_results = await asyncio.gather(*board_tasks)

    for board_result in board_results:
        results = sprint_planning_utils.merge_board_results(results, board_result)

    return results


@tool(
    requires_auth=Atlassian(
        scopes=[
            "read:sprint:jira-software",  # /sprint/{sprintId}/issue
            "read:issue-details:jira",  # /sprint/{sprintId}/issue
            "read:jql:jira",  # i/sprint/{sprintId}/issue
        ]
    )
)
async def get_sprint_issues(
    context: ToolContext,
    sprint_id: Annotated[
        str,
        "The numeric Jira sprint ID that identifies the sprint in Jira's API.",
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
        "Used for pagination when the sprint has many issues. "
        "Must be 0 or greater. Defaults to 0.",
    ] = 0,
    atlassian_cloud_id: Annotated[
        str | None,
        "The ID of the Atlassian Cloud to use (defaults to None). If not provided and the user has "
        "a single cloud authorized, the tool will use that. Otherwise, an error will be raised.",
    ] = None,
) -> Annotated[
    dict[str, Any],
    "A dictionary containing the sprint information, list of issues in the sprint, and pagination "
    "metadata.",
]:
    """
    Get all issues that are currently assigned to a specific sprint with pagination support.
    Returns issues that are planned for or being worked on in the sprint.
    """
    if not sprint_id:
        raise ToolExecutionError(SPRINT_ID_REQUIRED_ERROR)

    atlassian_cloud_id = await resolve_cloud_id(context, atlassian_cloud_id)
    client = JiraClient(context, atlassian_cloud_id, client_type=APIType.AGILE)
    limit = boards_utils.validate_board_limit(limit)

    try:
        issues_data, sprint_info = await sprint_planning_utils.fetch_sprint_issues_and_details(
            client, sprint_id, limit, offset
        )

        if issues_data.get("error"):
            return issues_data

        result = sprint_planning_utils.build_sprint_issues_result(
            sprint_id, issues_data["issues"], issues_data["is_last"], sprint_info
        )

        return add_pagination_to_response(result, result["issues"], limit, offset)

    except Exception as e:
        return sprint_planning_utils.create_sprint_issues_error_response(sprint_id, e)


@tool(
    requires_auth=Atlassian(
        scopes=[
            "write:sprint:jira-software",  # /sprint/{sprintId}/issue POST
            "read:sprint:jira-software",  # /sprint/{sprintId} GET, /sprint/{sprintId}/issue
            "read:board-scope:jira-software",  # /board/{boardId}/backlog (via dependencies)
            "read:issue-details:jira",  # issue details in responses (via dependencies)
            "read:jira-work",  # needed for get_issue_by_id calls
        ]
    )
)
async def add_issues_to_sprint(
    context: ToolContext,
    sprint_id: Annotated[
        str,
        "The numeric Jira sprint ID that identifies the sprint in Jira's API.",
    ],
    issue_ids: Annotated[
        list[str],
        "List of issue IDs or keys to add to the sprint. Must not be empty and cannot exceed 50 "
        "issues.",
    ],
    atlassian_cloud_id: Annotated[
        str | None,
        "The ID of the Atlassian Cloud to use (defaults to None). If not provided and the user has "
        "a single cloud authorized, the tool will use that. Otherwise, an error will be raised.",
    ] = None,
) -> Annotated[
    dict[str, Any],
    "A dictionary containing the results of adding issues to the sprint. "
    "Includes lists of successfully added issues, issues that were already in the sprint, "
    "issues not found, and issues that cannot be moved due to board restrictions. ",
]:
    """
    Add a list of issues to a sprint.
    Maximum of 50 issues per operation.
    """
    if not sprint_id:
        raise ToolExecutionError(SPRINT_ID_REQUIRED_ERROR)

    if not issue_ids:
        raise ToolExecutionError(ISSUE_IDS_REQUIRED_ERROR)

    atlassian_cloud_id = await resolve_cloud_id(context, atlassian_cloud_id)
    client = JiraClient(context, atlassian_cloud_id, client_type=APIType.AGILE)

    # Initialize result structure
    results: dict[str, Any] = {
        "sprint_id": sprint_id,
        "requested_issues": issue_ids,
        "successfully_added": [],
        "already_in_sprint": [],
        "not_found": [],
        "wrong_board": [],
        "errors": [],
    }

    try:
        sprint_details = await sprint_planning_utils.get_sprint_details(
            context=context,
            sprint_id=sprint_id,
            atlassian_cloud_id=atlassian_cloud_id,
        )

        if sprint_details.get("error"):
            return sprint_details

        validation_error = await sprint_planning_utils.validate_sprint_state_and_limits(
            sprint_id, issue_ids, sprint_details
        )
        if validation_error:
            return validation_error

        board_id = str(sprint_details["board_id"])

        current_state = await sprint_planning_utils.gather_sprint_and_backlog_state(
            context, sprint_id, board_id, atlassian_cloud_id
        )
        results["errors"].extend(current_state["errors"])

        (
            issues_to_add,
            classification_results,
        ) = await sprint_planning_utils.classify_issues_for_sprint(
            context,
            issue_ids,
            current_state["current_issue_ids"],
            current_state["backlog_issue_ids"],
            board_id,
            sprint_id,
            atlassian_cloud_id,
        )

        results = sprint_planning_utils.merge_classification_results(
            results, classification_results
        )

        if issues_to_add:
            try:
                successfully_added = await sprint_planning_utils.add_issues_to_sprint_api(
                    client, sprint_id, issues_to_add
                )
                results["successfully_added"] = successfully_added
            except Exception as e:
                results["errors"].append(str(e))

        results = sprint_planning_utils.add_result_summary(results)

    except Exception as e:
        return {
            "error": f"Unexpected error while adding issues to sprint '{sprint_id}': {e!s}",
            "sprint_id": sprint_id,
            "requested_issues": issue_ids,
        }
    else:
        return results


@tool(
    requires_auth=Atlassian(
        scopes=[
            "write:board-scope:jira-software",  # /backlog/issue POST
            "read:sprint:jira-software",  # /sprint/{sprintId}/issue, /sprint/{sprintId}
            "read:issue-details:jira",  # issue details in sprint responses
        ]
    )
)
async def move_issues_from_sprint_to_backlog(
    context: ToolContext,
    sprint_id: Annotated[
        str,
        "The numeric Jira sprint ID that identifies the sprint in Jira's API.",
    ],
    issue_identifiers: Annotated[
        list[str],
        "List of issue IDs or keys to move from the sprint to the backlog. "
        "Maximum 50 issues per call. "
        "Issues will be moved back to the board's backlog.",
    ],
    atlassian_cloud_id: Annotated[
        str | None,
        "The ID of the Atlassian Cloud to use (defaults to None). If not provided and the user has "
        "a single cloud authorized, the tool will use that. Otherwise, an error will be raised.",
    ] = None,
) -> Annotated[
    dict[str, Any],
    "A dictionary containing the sprint information, list of successfully removed issues, "
    "errors for issues that couldn't be removed, and backlog GUI URL. "
    "Issues are identified by ID or key and returned with available identifiers.",
]:
    """
    Move issues from active or future sprints back to the board's backlog.
    """
    if not sprint_id:
        raise ToolExecutionError(SPRINT_ID_REQUIRED_ERROR)

    if len(issue_identifiers) > 50:
        error_msg = f"{ISSUE_LIMIT_ERROR} You provided {len(issue_identifiers)} issues."
        raise ToolExecutionError(error_msg)

    if not issue_identifiers:
        raise ToolExecutionError(MISSING_ISSUE_IDENTIFIERS_ERROR)

    cloud_data = await resolve_cloud_id_and_name(context, atlassian_cloud_id)
    client = JiraClient(context, cloud_data["cloud_id"], client_type=APIType.AGILE)

    try:
        sprint_response, sprint_info = await sprint_planning_utils.fetch_sprint_issues_and_details(
            client,
            sprint_id,
            limit=1000,
            offset=0,
        )

        if sprint_response.get("error"):
            return sprint_response

        if sprint_info:
            state_validation_error = sprint_planning_utils.validate_sprint_state_for_removal(
                sprint_info
            )
            if state_validation_error:
                return state_validation_error

        result = await sprint_planning_utils.process_sprint_issue_removal(
            sprint_response, sprint_info, issue_identifiers, sprint_id, client, cloud_data
        )

    except Exception as e:
        return sprint_planning_utils.create_move_issues_error_response(
            sprint_id, issue_identifiers, e
        )
    else:
        return result
