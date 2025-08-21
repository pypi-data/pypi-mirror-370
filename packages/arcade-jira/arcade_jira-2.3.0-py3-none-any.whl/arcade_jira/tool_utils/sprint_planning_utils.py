"""Utility functions for sprint planning operations."""

import json
import logging
from datetime import datetime
from typing import Any, cast

from arcade_tdk import ToolContext
from arcade_tdk.errors import RetryableToolError, ToolExecutionError

from arcade_jira.client import JiraClient
from arcade_jira.constants import BOARD_TYPES_WITH_SPRINTS, SprintState
from arcade_jira.tool_utils import boards_utils
from arcade_jira.tools.boards import get_board_backlog_issues
from arcade_jira.utils import (
    build_base_jira_url,
    convert_date_string_to_date,
    create_error_entry,
    is_valid_date_string,
)

logger = logging.getLogger(__name__)

# Error message constants
BOARD_IDS_REQUIRED_ERROR = (
    "Board IDs are required. You must specify scrum boards to fetch sprint data."
)
CONFLICTING_DATE_PARAMS_ERROR = (
    "Cannot use 'specific_date' together with 'start_date' or 'end_date' parameters. "
    "Please use either specific_date alone or start_date/end_date for date range filtering."
)
SPECIFIC_DATE_FORMAT_ERROR = "Invalid specific_date format. Expected YYYY-MM-DD format."
START_DATE_FORMAT_ERROR = "Invalid start_date format. Expected YYYY-MM-DD format."
END_DATE_FORMAT_ERROR = "Invalid end_date format. Expected YYYY-MM-DD format."


def validate_parameters(
    specific_date: str | None,
    start_date: str | None,
    end_date: str | None,
    state: list[str] | None,
) -> None:
    """
    Validate input parameters for sprint listing.

    Raises:
        RetryableToolError: If parameters are invalid
    """
    # Validate date parameters
    if specific_date and (start_date or end_date):
        raise RetryableToolError(CONFLICTING_DATE_PARAMS_ERROR)

    # Validate date formats
    if specific_date and not is_valid_date_string(specific_date):
        raise RetryableToolError(SPECIFIC_DATE_FORMAT_ERROR)

    if start_date and not is_valid_date_string(start_date):
        raise RetryableToolError(START_DATE_FORMAT_ERROR)

    if end_date and not is_valid_date_string(end_date):
        raise RetryableToolError(END_DATE_FORMAT_ERROR)

    # Validate other parameters
    if state:
        _normalize_sprint_state(state)


def find_board_in_response(board_id: str, board_response: dict[str, Any]) -> dict[str, Any] | None:
    """
    Find a specific board from the board response that matches the given board_id.

    Args:
        board_id: Board identifier to search for
        board_response: Response from get_boards containing list of boards

    Returns:
        Board info dictionary if found, None otherwise
    """
    if not board_response["boards"]:
        return None

    for board in board_response["boards"]:
        # Check if board_id matches either the ID or name
        if (
            str(board["id"]) == str(board_id)
            or board.get("name", "").casefold() == board_id.casefold()
        ):
            return board  # type: ignore[no-any-return]
    return None


def handle_board_not_found(
    board_id: str, board_response: dict[str, Any], results: dict[str, Any]
) -> None:
    """
    Handle case when board is not found and add appropriate error to results.

    Args:
        board_id: Board identifier that wasn't found
        board_response: Response from get_boards
        results: Results dictionary to update with error
    """
    if board_response["errors"]:
        # Board not found, add the existing errors to our results
        results["errors"].extend(board_response["errors"])
    else:
        # Unexpected case - no boards and no errors
        error_entry = create_error_entry(
            board_id,
            f"Board '{board_id}' could not be resolved",
        )
        results["errors"].append(error_entry)


async def validate_sprint_state_and_limits(
    sprint_id: str, issue_ids: list[str], sprint_details: dict[str, Any]
) -> dict[str, Any] | None:
    """
    Validate sprint state and issue count limits.

    Returns:
        Error dictionary if validation fails, None if validation passes
    """
    board_id = sprint_details.get("board_id")
    sprint_state = sprint_details.get("sprint_state")

    if not board_id:
        return {
            "error": f"Could not determine board ID for sprint '{sprint_id}'.",
            "sprint_id": sprint_id,
        }

    # Check if sprint is in a valid state for adding issues
    if sprint_state not in ["active", "future"]:
        return {
            "error": (
                f"Issues can only be moved to active or future sprints. "
                f"Sprint '{sprint_id}' is in '{sprint_state}' state."
            ),
            "sprint_id": sprint_id,
            "sprint_state": sprint_state,
        }

    # Check maximum issues limit
    if len(issue_ids) > 50:
        return {
            "error": (
                f"Cannot move more than 50 issues in one operation. "
                f"You provided {len(issue_ids)} issues. "
                "Please split your request into smaller batches."
            ),
            "sprint_id": sprint_id,
            "total_issues_provided": len(issue_ids),
        }

    return None


async def get_current_sprint_and_backlog_issues(
    context: ToolContext, sprint_id: str, board_id: str, atlassian_cloud_id: str | None
) -> tuple[set[str], set[str], list[str]]:
    """
    Get current sprint issues and board backlog issues for validation.

    Returns:
        Tuple of (current_issue_ids, backlog_issue_ids, errors)
    """
    from arcade_jira.tools.sprint_planning import get_sprint_issues

    errors = []

    # Get current sprint issues to check for duplicates
    current_sprint_issues = await get_sprint_issues(
        context=context,
        sprint_id=sprint_id,
        limit=100,  # Get enough to check for duplicates
        atlassian_cloud_id=atlassian_cloud_id,
    )

    if current_sprint_issues.get("error"):
        errors.append(f"Failed to get current sprint issues: {current_sprint_issues['error']}")
        current_issue_ids = set()
    else:
        current_issue_ids = {issue["key"] for issue in current_sprint_issues.get("issues", [])}
        current_issue_ids.update({
            str(issue["id"]) for issue in current_sprint_issues.get("issues", [])
        })

    # Get board backlog to check if issues belong to the board
    board_backlog = await get_board_backlog_issues(
        context=context,
        board_id=board_id,
        limit=100,  # Get enough to check board membership
        atlassian_cloud_id=atlassian_cloud_id,
    )

    if board_backlog.get("error"):
        errors.append(f"Failed to get board backlog: {board_backlog['error']}")
        backlog_issue_ids = set()
    else:
        backlog_issue_ids = {issue["key"] for issue in board_backlog.get("issues", [])}
        backlog_issue_ids.update({str(issue["id"]) for issue in board_backlog.get("issues", [])})

    return current_issue_ids, backlog_issue_ids, errors


async def classify_issues_for_sprint(
    context: ToolContext,
    issue_ids: list[str],
    current_issue_ids: set[str],
    backlog_issue_ids: set[str],
    board_id: str,
    sprint_id: str,
    atlassian_cloud_id: str | None,
) -> tuple[list[str], dict[str, Any]]:
    """
    Classify issues into categories for sprint addition.

    Returns:
        Tuple of (issues_to_add, results_dict)
    """
    from arcade_jira.tools.issues import get_issue_by_id

    results: dict[str, Any] = {
        "successfully_added": [],
        "already_in_sprint": [],
        "not_found": [],
        "wrong_board": [],
        "errors": [],
    }

    issues_to_add = []

    for issue_id in issue_ids:
        # Check if already in sprint
        if issue_id in current_issue_ids:
            results["already_in_sprint"].append({
                "issue_id": issue_id,
                "message": f"Issue '{issue_id}' is already in sprint '{sprint_id}'.",
            })
            continue

        # Check if in board backlog (belongs to the same board)
        if issue_id in backlog_issue_ids:
            issues_to_add.append(issue_id)
            continue

        # Issue not in backlog or sprint - check if it exists and get its board info
        try:
            issue_response = await get_issue_by_id(
                context=context,
                issue=issue_id,
                atlassian_cloud_id=atlassian_cloud_id,
            )

            if issue_response.get("error"):
                results["not_found"].append({
                    "issue_id": issue_id,
                    "message": f"Issue '{issue_id}' not found: {issue_response['error']}",
                })
            else:
                # Issue exists but is not in the board backlog or sprint
                results["wrong_board"].append({
                    "issue_id": issue_id,
                    "message": (
                        f"Issue '{issue_id}' cannot be moved to sprint '{sprint_id}' "
                        f"because it does not belong to board '{board_id}'. "
                        "Issues can only be moved to sprints within the same board."
                    ),
                    "issue_project": (
                        issue_response["issue"].get("project", {}).get("key", "Unknown")
                    ),
                })

        except Exception as e:
            results["not_found"].append({
                "issue_id": issue_id,
                "message": f"Issue '{issue_id}' not found or not accessible: {e!s}",
            })

    return issues_to_add, results


# This large workflow function has been moved back to the tool for better visibility and testability


async def add_issues_to_sprint_api(
    client: JiraClient, sprint_id: str, issues_to_add: list[str]
) -> list[dict[str, Any]]:
    """
    Add issues to sprint via API call.

    Returns:
        List of successfully added issue results
    """
    ADD_ISSUES_FAILED_ERROR = "Failed to add issues to sprint"

    if not issues_to_add:
        return []

    try:
        # Jira API expects issues in the format: {"issues": ["ISSUE-1", "ISSUE-2"]}
        await client.post(f"/sprint/{sprint_id}/issue", json_data={"issues": issues_to_add})

        return [
            {
                "issue_id": issue_id,
                "message": f"Issue '{issue_id}' successfully added to sprint '{sprint_id}'.",
            }
            for issue_id in issues_to_add
        ]

    except Exception as e:
        raise ToolExecutionError(ADD_ISSUES_FAILED_ERROR) from e


async def process_board_sprints(
    client: JiraClient,
    board_info: dict[str, Any],
    board_id: str,
    offset: int,
    sprints_per_board: int,
    state: list[str] | None,
    start_date: str | None,
    end_date: str | None,
    specific_date: str | None,
    results: dict[str, Any],
) -> None:
    """
    Process sprints for a single board and add results.

    Args:
        client: JiraClient instance for API calls
        board_info: Board information dictionary
        board_id: Original board identifier
        offset: Number of sprints to skip
        sprints_per_board: Maximum sprints per board
        state: Optional state filter
        start_date: Optional start date filter
        end_date: Optional end date filter
        specific_date: Optional specific date filter
        results: Results dictionary to update
    """
    board_id_resolved = board_info["id"]

    # Check if board supports sprints and get final type, fetch sprints in one call
    params = _build_sprint_params(offset, sprints_per_board, state)
    supports_sprints, final_type, response = await try_fetch_sprints_and_determine_type(
        client, board_info, cast(dict[str, Any], params)
    )

    if not supports_sprints:
        error_entry = create_error_entry(
            board_id,
            f"Board '{board_info.get('name', board_id)}' does not support sprints "
            f"(type: {board_info.get('type', 'unknown')}). "
            f"Only Scrum boards support sprints.",
            board_info.get("name", "Unknown"),
            board_id_resolved,
        )
        results["errors"].append(error_entry)
        return

    # Update board type if it changed (simple -> scrum)
    board_info["type"] = final_type

    # Process the sprints we already fetched
    if response is None:
        # This should not happen if supports_sprints is True, but handle it gracefully
        error_entry = create_error_entry(
            board_id,
            f"Unexpected error: No sprint data received for board "
            f"'{board_info.get('name', board_id)}'",
            board_info.get("name", "Unknown"),
            board_id_resolved,
        )
        results["errors"].append(error_entry)
        return

    sprints = [_clean_sprint_dict(s) for s in response.get("values", [])]

    # Apply date filtering if specified
    if start_date or end_date or specific_date:
        sprints = _filter_sprints_by_date(sprints, start_date, end_date, specific_date)

    # Sort sprints with latest first (by end date, then start date, then ID)
    sprints = _sort_sprints_latest_first(sprints)

    results["boards"].append(board_info)
    results["sprints_by_board"][board_id_resolved] = _create_sprint_result_dict(
        board_info, sprints, response
    )


async def try_fetch_sprints_and_determine_type(
    client: JiraClient, board_info: dict[str, Any], params: dict[str, Any]
) -> tuple[bool, str, dict[str, Any] | None]:
    """
    Try to fetch sprints for a board and determine if it supports sprints.

    Args:
        client: JiraClient instance for API calls
        board_info: Board information dictionary
        params: Parameters for sprint API call

    Returns:
        Tuple of (supports_sprints, final_board_type, response)
    """
    board_id = board_info["id"]
    board_type = board_info.get("type", "").lower()

    # If already known to support sprints, fetch directly
    if board_type in BOARD_TYPES_WITH_SPRINTS:
        try:
            response = await client.get(f"/board/{board_id}/sprint", params=params)
        except Exception:
            return False, board_type, None
        else:
            return True, board_type, response

    # For 'simple' boards or unknown types, try fetching to see if it works
    try:
        response = await client.get(f"/board/{board_id}/sprint", params=params)
    except Exception:
        # Board doesn't support sprints
        return False, board_type, None
    else:
        # If successful, it's actually a scrum board
        return True, "scrum", response


async def get_sprint_details(
    context: ToolContext,
    sprint_id: str,
    atlassian_cloud_id: str | None = None,
) -> dict[str, Any]:
    """
    Get sprint details including board ID and state information.

    Args:
        context: Tool context for authentication
        sprint_id: Sprint ID to retrieve details for
        atlassian_cloud_id: Optional cloud ID

    Returns:
        Dictionary containing sprint details or error information
    """
    from arcade_jira.client import APIType
    from arcade_jira.utils import resolve_cloud_id

    atlassian_cloud_id = await resolve_cloud_id(context, atlassian_cloud_id)
    client = JiraClient(context, atlassian_cloud_id, client_type=APIType.AGILE)

    try:
        sprint_response = await client.get(f"/sprint/{sprint_id}")
        sprint_info = _clean_sprint_dict(sprint_response)
        return {
            "sprint": sprint_info,
            "board_id": sprint_info.get("originBoardId"),
            "sprint_state": sprint_info.get("state"),
        }
    except Exception as e:
        return {
            "error": f"Sprint with ID '{sprint_id}' not found or not accessible: {e!s}",
            "sprint_id": sprint_id,
        }


async def process_single_board(
    context: ToolContext,
    client: JiraClient,
    board_id: str,
    board_response: dict[str, Any],
    offset: int,
    max_sprints_per_board: int,
    state: list[str] | None,
    start_date: str | None,
    end_date: str | None,
    specific_date: str | None,
    cloud_name: str,
) -> dict[str, Any]:
    """
    Process a single board and return results without mutating input.

    Args:
        context: Tool context for authentication
        client: JiraClient instance for API calls
        board_id: Board identifier to process
        board_response: Board response from get_boards
        offset: Number of sprints to skip
        max_sprints_per_board: Maximum sprints per board
        state: Optional state filter
        start_date: Optional start date filter
        end_date: Optional end date filter
        specific_date: Optional specific date filter
        cloud_name: The name of the Atlassian Cloud to use for API calls

    Returns:
        Dictionary with processed results: {'boards': [...], 'sprints_by_board': {...},
        'errors': [...]}
    """
    # Initialize result structure (copy pattern)
    result: dict[str, Any] = {
        "boards": [],
        "sprints_by_board": {},
        "errors": [],
    }

    try:
        # Find the board in the response
        board_info = _find_board_in_response(board_id, board_response)

        if not board_info:
            _handle_board_not_found(board_id, board_response, result)
            return result

        # Process the board's sprints
        await _process_board_sprints(
            client,
            board_info,
            board_id,
            offset,
            max_sprints_per_board,
            state,
            start_date,
            end_date,
            specific_date,
            result,
            cloud_name,
        )

    except ToolExecutionError:
        # Re-raise ToolExecutionErrors as-is
        raise
    except Exception as e:
        error_entry = create_error_entry(
            board_id,
            f"Unexpected error processing board '{board_id}': {e!s}",
        )
        result["errors"].append(error_entry)

    return result


def validate_sprint_limit(limit: int) -> int:
    """
    Validate and normalize sprint limit parameter.

    Args:
        limit: Raw limit value

    Returns:
        Normalized limit value (1-50)
    """
    return max(1, min(limit, 50))


async def gather_sprint_and_backlog_state(
    context: ToolContext, sprint_id: str, board_id: str, atlassian_cloud_id: str | None
) -> dict[str, Any]:
    """
    Gather current sprint and backlog state in a functional manner.

    Returns:
        Dictionary with current_issue_ids, backlog_issue_ids, and errors
    """
    current_issue_ids, backlog_issue_ids, errors = await get_current_sprint_and_backlog_issues(
        context, sprint_id, board_id, atlassian_cloud_id
    )

    return {
        "current_issue_ids": current_issue_ids,
        "backlog_issue_ids": backlog_issue_ids,
        "errors": errors,
    }


def add_result_summary(result: dict[str, Any]) -> dict[str, Any]:
    """
    Add summary statistics to result (pure function).

    Args:
        result: Result dictionary to add summary to

    Returns:
        Result dictionary with summary added
    """
    final_result = result.copy()
    final_result["summary"] = {
        "total_requested": len(result["requested_issues"]),
        "successfully_added": len(result["successfully_added"]),
        "already_in_sprint": len(result["already_in_sprint"]),
        "not_found": len(result["not_found"]),
        "wrong_board": len(result["wrong_board"]),
        "errors": len(result["errors"]),
    }
    return final_result


def merge_classification_results(
    base_result: dict[str, Any], classification_results: dict[str, Any]
) -> dict[str, Any]:
    """
    Merge classification results into base result (pure function).

    Args:
        base_result: Base result dictionary
        classification_results: Classification results to merge

    Returns:
        Merged result dictionary
    """
    result = base_result.copy()
    for key in ["already_in_sprint", "not_found", "wrong_board", "errors"]:
        if key in classification_results:
            result[key].extend(classification_results[key])
    return result


async def fetch_sprint_issues_and_details(
    client: JiraClient, sprint_id: str, limit: int, offset: int
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    """
    Fetch sprint issues and details concurrently (functional approach).

    Args:
        client: JiraClient for API calls
        sprint_id: Sprint ID to fetch data for
        limit: Maximum number of issues
        offset: Pagination offset

    Returns:
        Tuple of (issues_data, sprint_info)
    """
    import logging

    from arcade_jira.utils import clean_issue_dict

    logger = logging.getLogger(__name__)

    try:
        # Fetch issues from sprint
        response = await client.get(
            f"/sprint/{sprint_id}/issue",
            params={
                "startAt": offset,
                "maxResults": limit,
                "expand": "renderedFields",
            },
        )

        issues = [clean_issue_dict(issue) for issue in response.get("issues", [])]
        issues_data = {
            "issues": issues,
            "is_last": response.get("isLast", False),
        }

        # Try to get sprint details for additional context
        sprint_info = await _get_sprint_info_safely(client, sprint_id, logger)

    except Exception as e:
        error_message = f"Failed to retrieve issues for sprint '{sprint_id}': {e!s}"
        if "404" in str(e) or "not found" in str(e).lower():
            error_message = f"Sprint with ID '{sprint_id}' not found or not accessible."

        return {"error": error_message, "sprint_id": sprint_id}, None
    else:
        return issues_data, sprint_info


def build_sprint_issues_result(
    sprint_id: str, issues: list[dict], is_last: bool, sprint_info: dict[str, Any] | None
) -> dict[str, Any]:
    """
    Build sprint issues result dictionary (pure function).

    Args:
        sprint_id: Sprint ID
        issues: List of issue dictionaries
        is_last: Whether this is the last page
        sprint_info: Sprint information (optional)

    Returns:
        Result dictionary
    """
    result = {
        "sprint_id": sprint_id,
        "issues": issues,
        "isLast": is_last,
    }

    if sprint_info:
        result["sprint"] = sprint_info

    return result


def create_sprint_issues_error_response(sprint_id: str, error: Exception) -> dict[str, Any]:
    """
    Create error response for sprint issues (pure function).

    Args:
        sprint_id: Sprint ID that failed
        error: Exception that occurred

    Returns:
        Error response dictionary
    """
    error_message = f"Failed to retrieve issues for sprint '{sprint_id}': {error!s}"
    if "404" in str(error) or "not found" in str(error).lower():
        error_message = f"Sprint with ID '{sprint_id}' not found or not accessible."

    return {
        "error": error_message,
        "sprint_id": sprint_id,
    }


def determine_boards_to_process(
    board_identifiers_list: list[str] | None, board_response: dict[str, Any]
) -> list[str]:
    """
    Determine which boards to process (pure function).

    Args:
        board_identifiers_list: Original board identifiers list
        board_response: Response from get_boards

    Returns:
        List of board IDs to process
    """
    return (
        board_identifiers_list
        if board_identifiers_list
        else [str(board["id"]) for board in board_response.get("boards", [])]
    )


# This private workflow function has been moved back to the tool for better testability


def merge_board_results(
    accumulated_result: dict[str, Any], board_result: dict[str, Any]
) -> dict[str, Any]:
    """
    Merge board results into accumulated result (pure function).

    Args:
        accumulated_result: Current accumulated results
        board_result: Results from processing a single board

    Returns:
        Merged result dictionary
    """
    merged = accumulated_result.copy()
    merged["boards"].extend(board_result["boards"])
    merged["sprints_by_board"].update(board_result["sprints_by_board"])
    merged["errors"].extend(board_result["errors"])
    return merged


async def _get_sprint_info_safely(
    client: JiraClient, sprint_id: str, logger: logging.Logger
) -> dict[str, Any] | None:
    """
    Safely get sprint information, returning None if not available.

    Args:
        client: JiraClient for API calls
        sprint_id: Sprint ID to fetch
        logger: Logger instance for debug messages

    Returns:
        Sprint info dictionary or None if not available
    """
    try:
        sprint_response = await client.get(f"/sprint/{sprint_id}")
        return _clean_sprint_dict(sprint_response)
    except Exception:
        # Sprint details not available, but issues might still be retrievable
        logger.debug(f"Could not fetch sprint details for sprint {sprint_id}")
        return None


def validate_sprint_state_for_removal(sprint_details: dict[str, Any]) -> dict[str, Any] | None:
    """
    Validate if a sprint allows issue removal based on documentation.

    Based on Atlassian documentation, issues can be moved from active and future sprints to backlog.

    Args:
        sprint_details: Sprint information including state

    Returns:
        Error dictionary if validation fails, None if validation passes
    """
    sprint_state = sprint_details.get("state", "").lower()
    sprint_id = sprint_details.get("id")

    # Allow removal from active and future sprints based on Atlassian documentation
    # Only prevent removal from closed sprints
    if sprint_state == "closed":
        return {
            "error": f"Cannot move issues from closed sprint '{sprint_id}' to backlog. "
            "Issues can only be moved from active or future sprints.",
            "sprint_id": str(sprint_id),
            "sprint_state": sprint_state,
        }

    # Allow removal from active and future sprints
    if sprint_state in ["active", "future"]:
        return None

    return None


async def process_sprint_issue_removal(
    sprint_response: dict[str, Any],
    sprint_info: dict[str, Any] | None,
    issue_identifiers: list[str],
    sprint_id: str,
    client: JiraClient,
    cloud_data: dict[str, Any],
) -> dict[str, Any]:
    """Process the complete removal workflow for sprint issues."""
    # Find which issues are actually in the sprint
    sprint_issues = sprint_response.get("issues", [])
    matched_issues, not_found_identifiers = _find_issues_in_sprint(issue_identifiers, sprint_issues)

    # Build response structure
    result: dict[str, Any] = {
        "sprint_id": sprint_id,
        "successfully_removed": [],
        "errors": [],
    }

    # Add sprint information if available
    if sprint_info:
        result["sprint"] = sprint_info

    # Handle issues not found in sprint
    for identifier in not_found_identifiers:
        result["errors"].append({
            "issue_identifier": identifier,
            "error": (
                f"Issue '{identifier}' does not belong to sprint '{sprint_id}' or was not found."
            ),
        })

    # Attempt to remove found issues
    if matched_issues:
        await _process_issue_removal(result, matched_issues, client)

    # Add GUI URLs if we have sprint info
    if sprint_info:
        board_id = sprint_info.get("originBoardId")
        if board_id and cloud_data["cloud_name"]:
            _build_gui_urls_for_sprint(
                result, cloud_data["cloud_name"], board_id, sprint_id, sprint_issues
            )

    return result


def create_move_issues_error_response(
    sprint_id: str, issue_identifiers: list[str], error: Exception
) -> dict[str, Any]:
    """Create error response for move_issues_from_sprint_to_backlog tool."""
    return {
        "error": (
            f"Unexpected error while moving issues from sprint '{sprint_id}' to backlog: {error!s}"
        ),
        "sprint_id": sprint_id,
        "requested_issues": issue_identifiers,
    }


# Private helper functions (used only within this module)
async def _process_issue_removal(
    result: dict[str, Any], matched_issues: list[dict[str, Any]], client: JiraClient
) -> None:
    """Process the removal of matched issues from sprint."""
    # Extract identifiers for API call (prefer keys over IDs)
    identifiers_to_remove = []
    for issue in matched_issues:
        if "key" in issue:
            identifiers_to_remove.append(issue["key"])
        elif "id" in issue:
            identifiers_to_remove.append(str(issue["id"]))

    # Call removal API
    removal_result = await _remove_issues_from_sprint_api(client, identifiers_to_remove)

    if removal_result["success"]:
        # Build success entries with available identifiers
        for issue in matched_issues:
            success_entry = {}
            if "id" in issue:
                success_entry["id"] = issue["id"]
            if "key" in issue:
                success_entry["key"] = issue["key"]
            if "summary" in issue:
                success_entry["summary"] = issue["summary"]

            result["successfully_removed"].append(success_entry)
    else:
        # API call failed - add all as errors
        for issue in matched_issues:
            identifier = issue.get("key", str(issue.get("id", "unknown")))
            result["errors"].append({
                "issue_identifier": identifier,
                "error": removal_result["error"],
            })


def _build_gui_urls_for_sprint(
    result: dict[str, Any],
    cloud_name: str,
    board_id: int,
    sprint_id: str,
    sprint_issues: list[dict[str, Any]],
) -> None:
    """Add GUI URLs to the result if project information is available."""
    project_key = None
    if sprint_issues:
        first_issue = sprint_issues[0]
        if "project" in first_issue and "key" in first_issue["project"]:
            project_key = first_issue["project"]["key"]

    # Build backlog URL
    result["backlog_jira_gui_url"] = _build_backlog_url(cloud_name, str(board_id), project_key)


def _build_backlog_url(
    cloud_name: str | None, board_id: str, project_key: str | None = None
) -> str | None:
    """Build a URL to a Jira board's backlog."""
    base_url = build_base_jira_url(cloud_name)
    if not base_url or not board_id or not project_key:
        return None

    return f"{base_url}/jira/software/projects/{project_key}/boards/{board_id}/backlog"


def _build_sprint_params(
    offset: int, max_results: int, state: list[str] | None = None
) -> dict[str, str]:
    """
    Build parameters for sprint API calls.

    Args:
        offset: Number of sprints to skip
        max_results: Maximum number of sprints to return
        state: Optional state filter list

    Returns:
        Dictionary of parameters for sprint API call
    """
    params = {
        "startAt": str(int(offset)),
        "maxResults": str(int(max_results)),
    }
    if state:
        # Convert list to comma-separated string for API
        params["state"] = ",".join(state)
    return params


def _clean_sprint_dict(sprint: dict, cloud_name: str | None = None) -> dict:
    """
    Clean and standardize a sprint dictionary.

    Args:
        sprint: Raw sprint data from Jira API
        cloud_name: Optional cloud name for building jira_gui_url

    Returns:
        Cleaned sprint dictionary with essential fields
    """
    cleaned = {
        "id": sprint["id"],
        "name": sprint["name"],
        "state": sprint.get("state"),
        "startDate": sprint.get("startDate"),
        "endDate": sprint.get("endDate"),
        "completeDate": sprint.get("completeDate"),
        "originBoardId": sprint.get("originBoardId"),
        "goal": sprint.get("goal"),
    }

    return cleaned


def _create_sprint_result_dict(
    board: dict, sprints: list[dict], response: dict, cloud_name: str | None = None
) -> dict[str, Any]:
    """
    Create a standardized result dictionary for sprint operations.

    Args:
        board: Board dictionary
        sprints: List of sprint dictionaries
        response: Raw API response
        cloud_name: Optional cloud name for building jira_gui_url

    Returns:
        Standardized result dictionary
    """
    # Calculate next_offset as current_offset + min(limit, items_returned_count)
    current_offset = response.get("startAt", 0)
    max_results = response.get("maxResults", 0)
    items_returned_count = len(sprints)
    next_offset = current_offset + min(max_results, items_returned_count)

    result = {
        "board": boards_utils.clean_board_dict(board, cloud_name),
        "sprints": sprints,
        "is_last": response.get("isLast"),
        "total": response.get("total"),
    }

    # Only include pagination details if there are more pages
    if not response.get("isLast"):
        result.update({
            "current_offset": current_offset,
            "max_results": max_results,
            "next_offset": next_offset,
        })

    # Add backlog URL if cloud_name is provided
    if cloud_name:
        # Try to extract project key from board data
        project_key = None
        if "location" in board and "projectKey" in board["location"]:
            project_key = board["location"]["projectKey"]
        elif "project" in board and "key" in board["project"]:
            project_key = board["project"]["key"]
        elif "jira_gui_url" in board:
            # Extract project key from existing GUI URL as fallback
            # URL format: https://domain.atlassian.net/jira/software/projects/PROJECT_KEY/boards/ID
            gui_url = board["jira_gui_url"]
            if "/projects/" in gui_url and "/boards/" in gui_url:
                try:
                    project_key = gui_url.split("/projects/")[1].split("/boards/")[0]
                except (IndexError, AttributeError):
                    project_key = None

        backlog_url = _build_backlog_url(cloud_name, str(board["id"]), project_key)
        if backlog_url:
            result["jira_backlog_gui_url"] = backlog_url

    return result


def _find_board_in_response(board_id: str, board_response: dict[str, Any]) -> dict[str, Any] | None:
    """
    Find a specific board from the board response that matches the given board_id.

    Args:
        board_id: Board identifier to search for
        board_response: Response from get_boards containing list of boards

    Returns:
        Board info dictionary if found, None otherwise
    """
    if not board_response["boards"]:
        return None

    for board in board_response["boards"]:
        # Check if board_id matches either the ID or name
        if (
            str(board["id"]) == str(board_id)
            or board.get("name", "").casefold() == board_id.casefold()
        ):
            return board  # type: ignore[no-any-return]
    return None


def _handle_board_not_found(
    board_id: str, board_response: dict[str, Any], results: dict[str, Any]
) -> None:
    """
    Handle case when board is not found and add appropriate error to results.

    Args:
        board_id: Board identifier that wasn't found
        board_response: Response from get_boards
        results: Results dictionary to update with error
    """
    if board_response["errors"]:
        # Board not found, add the existing errors to our results
        results["errors"].extend(board_response["errors"])
    else:
        # Unexpected case - no boards and no errors
        error_entry = create_error_entry(
            board_id,
            f"Board '{board_id}' could not be resolved",
        )
        results["errors"].append(error_entry)


def _normalize_sprint_state(state: list[str] | None) -> list[str] | None:
    """
    Normalize sprint state parameter against allowed values.

    Args:
        state: List of sprint state strings

    Returns:
        Normalized state list unchanged if valid

    Raises:
        RetryableToolError: If any state values are invalid
    """
    if not state:
        return state

    # Clean and normalize state values
    state_values = [s.strip().lower() for s in state if s.strip()]

    if not state_values:
        return None

    # Get valid state values
    valid_states = SprintState.get_valid_values()

    # Check for invalid states
    invalid_states = [s for s in state_values if s not in valid_states]

    if invalid_states:
        invalid_states_str = ", ".join(f"'{state}'" for state in invalid_states)
        valid_states_json = json.dumps(valid_states, default=str)

        message = f"Invalid sprint state(s): {invalid_states_str}."
        additional_message = f"Valid sprint states are: {valid_states_json}"
        raise RetryableToolError(message, additional_prompt_content=additional_message)

    return state


async def _process_board_sprints(
    client: JiraClient,
    board_info: dict[str, Any],
    board_id: str,
    offset: int,
    max_sprints_per_board: int,
    state: list[str] | None,
    start_date: str | None,
    end_date: str | None,
    specific_date: str | None,
    results: dict[str, Any],
    cloud_name: str,
) -> None:
    """
    Process sprints for a single board and add results.

    Args:
        client: JiraClient instance for API calls
        board_info: Board information dictionary
        board_id: Original board identifier
        offset: Number of sprints to skip
        max_sprints_per_board: Maximum sprints per board
        state: Optional state filter
        start_date: Optional start date filter
        end_date: Optional end date filter
        specific_date: Optional specific date filter
        results: Results dictionary to update
        cloud_name: The name of the Atlassian Cloud to use for API calls
    """
    board_id_resolved = board_info["id"]

    # Check if board supports sprints and get final type, fetch sprints in one call
    params = _build_sprint_params(offset, max_sprints_per_board, state)
    supports_sprints, final_type, response = await _try_fetch_sprints_and_determine_type(
        client, board_info, cast(dict[str, Any], params)
    )

    if not supports_sprints:
        error_entry = create_error_entry(
            board_id,
            f"Board '{board_info.get('name', board_id)}' does not support sprints "
            f"(type: {board_info.get('type', 'unknown')}). "
            f"Only Scrum boards support sprints.",
            board_info.get("name", "Unknown"),
            board_id_resolved,
        )
        results["errors"].append(error_entry)
        return

    # Update board type if it changed (simple -> scrum)
    board_info["type"] = final_type

    # Process the sprints we already fetched
    if response is None:
        # This should not happen if supports_sprints is True, but handle it gracefully
        error_entry = create_error_entry(
            board_id,
            f"Unexpected error: No sprint data received for board "
            f"'{board_info.get('name', board_id)}'",
            board_info.get("name", "Unknown"),
            board_id_resolved,
        )
        results["errors"].append(error_entry)
        return

    sprints = [_clean_sprint_dict(s, cloud_name) for s in response.get("values", [])]

    # Apply date filtering if specified
    if start_date or end_date or specific_date:
        sprints = _filter_sprints_by_date(sprints, start_date, end_date, specific_date)

    # Sort sprints with latest first (by end date, then start date, then ID)
    sprints = _sort_sprints_latest_first(sprints)

    results["boards"].append(board_info)
    results["sprints_by_board"][board_id_resolved] = _create_sprint_result_dict(
        board_info, sprints, response, cloud_name
    )


async def _try_fetch_sprints_and_determine_type(
    client: JiraClient, board_info: dict[str, Any], params: dict[str, Any]
) -> tuple[bool, str, dict[str, Any] | None]:
    """
    Try to fetch sprints for a board and determine if it supports sprints.

    Args:
        client: JiraClient instance for API calls
        board_info: Board information dictionary
        params: Query parameters for the sprint request

    Returns:
        Tuple of (supports_sprints, final_board_type, response_or_none)
    """
    board_id = board_info["id"]
    board_type = board_info.get("type", "").lower()

    try:
        response = await client.get(f"/board/{board_id}/sprint", params=params)
    except Exception:
        # Board doesn't support sprints
        return False, board_type, None
    else:
        # If successful, it's actually a scrum board
        return True, "scrum", response


def _filter_sprints_by_date(
    sprints: list[dict], start_date: str | None, end_date: str | None, specific_date: str | None
) -> list[dict]:
    """
    Filter sprints by date range or specific date.

    Args:
        sprints: List of sprint dictionaries
        start_date: Start date string in YYYY-MM-DD format
        end_date: End date string in YYYY-MM-DD format
        specific_date: Specific date string in YYYY-MM-DD format

    Returns:
        Filtered list of sprints
    """
    if not sprints:
        return sprints

    if specific_date:
        return _filter_sprints_by_specific_date(sprints, specific_date)
    elif start_date or end_date:
        return _filter_sprints_by_date_range(sprints, start_date, end_date)

    return sprints


def _filter_sprints_by_specific_date(sprints: list[dict], target_date: str) -> list[dict]:
    """
    Filter sprints that are active on a specific date.

    Args:
        sprints: List of sprint dictionaries
        target_date: Target date string in YYYY-MM-DD format

    Returns:
        Filtered list of sprints
    """
    # Date validation is done at tool entry, so we can parse directly
    target = convert_date_string_to_date(target_date)

    filtered_sprints = []
    for sprint in sprints:
        start_date_str = sprint.get("startDate")
        end_date_str = sprint.get("endDate")

        # Skip sprints without dates
        if not start_date_str or not end_date_str:
            continue

        # Parse Jira date format (ISO format with timezone)
        start_date = datetime.fromisoformat(start_date_str.replace("Z", "+00:00")).date()
        end_date = datetime.fromisoformat(end_date_str.replace("Z", "+00:00")).date()

        # Check if target date is within sprint dates
        if start_date <= target <= end_date:
            filtered_sprints.append(sprint)

    return filtered_sprints


def _filter_sprints_by_date_range(
    sprints: list[dict], start_date: str | None, end_date: str | None
) -> list[dict]:
    """
    Filter sprints that overlap with the specified date range.

    Args:
        sprints: List of sprint dictionaries
        start_date: Start date string in YYYY-MM-DD format
        end_date: End date string in YYYY-MM-DD format

    Returns:
        Filtered list of sprints
    """
    # Date validation is done at tool entry, so we can parse directly
    filter_start = convert_date_string_to_date(start_date) if start_date else None
    filter_end = convert_date_string_to_date(end_date) if end_date else None

    filtered_sprints = []
    for sprint in sprints:
        start_date_str = sprint.get("startDate")
        end_date_str = sprint.get("endDate")

        # Skip sprints without dates if we have date filters
        if (filter_start or filter_end) and (not start_date_str or not end_date_str):
            continue

        # Parse Jira date format (ISO format with timezone)
        sprint_start = (
            datetime.fromisoformat(start_date_str.replace("Z", "+00:00")).date()
            if start_date_str
            else None
        )
        sprint_end = (
            datetime.fromisoformat(end_date_str.replace("Z", "+00:00")).date()
            if end_date_str
            else None
        )

        # Check if sprint overlaps with filter range
        overlap = True

        if filter_start and sprint_end and sprint_end < filter_start:
            overlap = False

        if filter_end and sprint_start and sprint_start > filter_end:
            overlap = False

        if overlap:
            filtered_sprints.append(sprint)

    return filtered_sprints


def _sort_sprints_latest_first(sprints: list[dict]) -> list[dict]:
    """
    Sort sprints with latest first (by end date, start date, then ID).

    Args:
        sprints: List of sprint dictionaries

    Returns:
        Sorted list of sprints with latest first
    """
    from datetime import date as min_date

    def sort_key(sprint: dict) -> tuple:
        end_date_str = sprint.get("endDate")
        start_date_str = sprint.get("startDate")
        sprint_id = sprint.get("id")

        try:
            end_date = (
                datetime.fromisoformat(end_date_str.replace("Z", "+00:00")).date()
                if end_date_str
                else min_date.min
            )
        except (ValueError, AttributeError):
            end_date = min_date.min

        try:
            start_date = (
                datetime.fromisoformat(start_date_str.replace("Z", "+00:00")).date()
                if start_date_str
                else min_date.min
            )
        except (ValueError, AttributeError):
            start_date = min_date.min

        return (
            -end_date.toordinal() if end_date != min_date.min else float("inf"),
            -start_date.toordinal() if start_date != min_date.min else float("inf"),
            -int(sprint_id) if isinstance(sprint_id, int | str) and str(sprint_id).isdigit() else 0,
        )

    return sorted(sprints, key=sort_key)


def _find_issues_in_sprint(
    issue_identifiers: list[str], sprint_issues: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], list[str]]:
    """
    Find which input identifiers match issues in the sprint.

    Args:
        issue_identifiers: List of issue IDs, keys, or other identifiers
        sprint_issues: List of issue dictionaries from sprint

    Returns:
        Tuple of (matched_issues, not_found_identifiers)
    """
    # Deduplicate input identifiers
    unique_identifiers = list(dict.fromkeys(issue_identifiers))

    matched_issues = []
    not_found_identifiers = []

    # Build lookup sets for efficient matching
    issue_lookup = {}
    for issue in sprint_issues:
        # Add by ID
        if "id" in issue:
            issue_lookup[str(issue["id"])] = issue
        # Add by key
        if "key" in issue:
            issue_lookup[issue["key"]] = issue

    for identifier in unique_identifiers:
        if identifier in issue_lookup:
            issue = issue_lookup[identifier]
            # Only add once even if matched by multiple fields
            if issue not in matched_issues:
                matched_issues.append(issue)
        else:
            not_found_identifiers.append(identifier)

    return matched_issues, not_found_identifiers


async def _remove_issues_from_sprint_api(
    client: JiraClient, issue_identifiers: list[str]
) -> dict[str, Any]:
    """
    Call Jira API to move issues from sprint to backlog.

    Args:
        client: JiraClient for API calls
        issue_identifiers: List of issue IDs/keys to move to backlog

    Returns:
        API response or error dictionary
    """
    try:
        response = await client.post("/backlog/issue", json_data={"issues": issue_identifiers})
    except Exception as e:
        return {"success": False, "error": f"Failed to move issues from sprint to backlog: {e!s}"}
    else:
        return {"success": True, "response": response}
