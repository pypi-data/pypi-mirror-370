"""Utility functions for board operations."""

import logging
from typing import Any

from arcade_jira.client import JiraClient
from arcade_jira.utils import (
    build_base_jira_url,
    create_error_entry,
)

logger = logging.getLogger(__name__)


async def get_boards_by_identifiers(
    client: JiraClient,
    board_identifiers: list[str],
    cloud_name: str,
    limit: int = 50,
    offset: int = 0,
) -> dict[str, Any]:
    """
    Get boards by specific identifiers with deduplication logic.

    Args:
        client: JiraClient instance for API calls
        board_identifiers: List of board names or IDs to retrieve
        cloud_name: The name of the Atlassian Cloud to use for API calls

    Returns:
        Dictionary containing deduplicated boards and any errors
    """
    results: dict[str, Any] = {
        "boards": [],
        "errors": [],
    }

    # Track processed identifiers (both IDs and names) to prevent duplicates
    processed_identifiers = set()

    for board_identifier in board_identifiers:
        # Skip if we already processed this identifier or found this board
        if board_identifier in processed_identifiers:
            continue

        try:
            board_result = await _find_board_by_identifier(client, board_identifier, cloud_name)

            if board_result:
                # Add both the board ID and name to processed set to prevent future duplicates
                processed_identifiers.add(str(board_result["id"]))
                processed_identifiers.add(board_result["name"])
                results["boards"].append(board_result)
            else:
                # Board not found, add to errors
                error_entry = create_error_entry(
                    board_identifier,
                    f"Board '{board_identifier}' not found",
                )
                results["errors"].append(error_entry)

        except Exception as e:
            error_entry = create_error_entry(
                board_identifier,
                f"Unexpected error processing board '{board_identifier}': {e!s}",
            )
            results["errors"].append(error_entry)

    items_returned_count = len(results["boards"])
    results["next_offset"] = offset + min(limit, items_returned_count)

    return results


async def get_boards_with_offset(
    client: JiraClient,
    limit: int,
    offset: int,
    cloud_name: str,
) -> dict[str, Any]:
    """
    Get all boards with pagination using Jira API parameters.

    Args:
        client: JiraClient instance for API calls
        limit: Maximum number of boards to return
        offset: Number of boards to skip

    Returns:
        Dictionary containing boards and pagination metadata
    """
    response = await client.get(
        "/board",
        params={
            "startAt": offset,
            "maxResults": limit,
        },
    )

    boards = [clean_board_dict(board, cloud_name) for board in response.get("values", [])]

    return _create_board_result_dict(
        boards,
        len(boards),
        response.get("isLast", False),
        offset,
        limit,
        cloud_name,
    )


def validate_board_limit(limit: int) -> int:
    """
    Validate and normalize board limit parameter.

    Args:
        limit: Raw limit value

    Returns:
        Normalized limit value (1-50)
    """
    return max(1, min(limit, 50))


def _build_board_url(
    cloud_name: str | None, board_id: str, project_key: str | None = None
) -> str | None:
    """Build a URL to a Jira board."""
    base_url = build_base_jira_url(cloud_name)
    if not base_url or not board_id or not project_key:
        return None

    return f"{base_url}/jira/software/projects/{project_key}/boards/{board_id}"


def clean_board_dict(board: dict, cloud_name: str | None = None) -> dict:
    """
    Clean and standardize a board dictionary.

    Args:
        board: Raw board data from Jira API
        cloud_name: Optional cloud name for building jira_gui_url

    Returns:
        Cleaned board dictionary with essential fields
    """
    cleaned = {
        "id": board["id"],
        "name": board["name"],
        "type": board.get("type"),
        "self": board.get("self"),
    }

    if "jira_gui_url" in board:
        cleaned["jira_gui_url"] = board["jira_gui_url"]
    elif cloud_name:
        project_key = None
        if "location" in board and "projectKey" in board["location"]:
            project_key = board["location"]["projectKey"]
        elif "project" in board and "key" in board["project"]:
            project_key = board["project"]["key"]

        cleaned["jira_gui_url"] = _build_board_url(cloud_name, str(board["id"]), project_key)

    return cleaned


def _create_board_result_dict(
    boards: list[dict],
    total: int,
    is_last: bool,
    start_at: int,
    max_results: int,
    cloud_name: str | None = None,
) -> dict[str, Any]:
    """
    Create a standardized result dictionary for board operations.

    Args:
        boards: List of board dictionaries
        total: Total number of boards
        is_last: Whether this is the last page
        current_at: Starting offset
        max_results: Maximum results per page
        cloud_name: Optional cloud name for building jira_gui_url

    Returns:
        Standardized result dictionary
    """
    items_returned_count = len(boards)
    next_offset = start_at + min(max_results, items_returned_count)

    result = {
        "boards": [clean_board_dict(b, cloud_name) for b in boards],
        "total": total,
        "is_last": is_last,
    }

    if not is_last:
        result.update({
            "current_offset": start_at,
            "max_results": max_results,
            "next_offset": next_offset,
        })

    return result


async def _find_board_by_identifier(
    client: JiraClient,
    board_identifier: str,
    cloud_name: str,
) -> dict[str, Any] | None:
    """
    Find a board by either ID or name.

    Args:
        client: JiraClient instance for API calls
        board_identifier: Board ID or name to search for
        cloud_name: The name of the Atlassian Cloud to use for API calls

    Returns:
        Cleaned board dictionary if found, None otherwise
    """
    # If identifier is numeric, try to get by ID first
    if board_identifier.isdigit():
        board_result = await _find_board_by_id(client, board_identifier, cloud_name)
        if board_result:
            return board_result
        # ID lookup failed, fall back to name lookup
        logger.warning(f"Board ID lookup failed for '{board_identifier}'. Attempting name lookup.")

    # Try by name (for non-numeric identifiers or failed ID lookup)
    return await _find_board_by_name(client, board_identifier, cloud_name)


async def _find_board_by_id(
    client: JiraClient,
    board_id: str,
    cloud_name: str,
) -> dict[str, Any] | None:
    """
    Find a board by its ID.

    Args:
        client: JiraClient instance for API calls
        board_id: Board ID to search for
        cloud_name: The name of the Atlassian Cloud to use for API calls

    Returns:
        Cleaned board dictionary if found, None otherwise
    """
    try:
        board = await client.get(f"/board/{board_id}")
    except Exception:
        logger.warning(f"Board ID lookup failed for '{board_id}'. API error.")
        return None
    else:
        board_result = clean_board_dict(board, cloud_name)
        board_result["found_by"] = "id"
        return board_result


async def _find_board_by_name(
    client: JiraClient,
    board_name: str,
    cloud_name: str,
) -> dict[str, Any] | None:
    """
    Find a board by its name using Jira API name filter.

    Args:
        client: JiraClient instance for API calls
        board_name: Board name to search for
        cloud_name: The name of the Atlassian Cloud to use for API calls

    Returns:
        Cleaned board dictionary if found, None otherwise
    """
    try:
        response = await client.get(
            "/board",
            params={
                "name": board_name,
                "startAt": 0,
                "maxResults": 1,
            },
        )

        boards = response.get("values", [])
        if boards:
            board_result = clean_board_dict(boards[0], cloud_name)
            board_result["found_by"] = "name"
            return board_result
    except Exception:
        logger.warning(f"Board name lookup failed for '{board_name}'. API error.")

    return None
