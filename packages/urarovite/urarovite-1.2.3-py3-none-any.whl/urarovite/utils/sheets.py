"""Google Sheets utilities for data access and manipulation.

This module provides utilities for working with Google Sheets, including
URL parsing, range handling, and data retrieval. Enhanced from the original
checker/utils.py with better error handling, exponential backoff, and additional functionality.

Range Separator Configuration:
    The module supports configurable range separators for parsing verification field ranges.
    By default, ranges are separated by '@@', but this can be changed globally or per-call.

    Examples:
        >>> from urarovite.utils.sheets import set_segment_separator, split_segments
        >>> set_segment_separator(",")
        >>> split_segments("A1,B2,C3")  # Uses comma separator
        ['A1', 'B2', 'C3']
        >>> split_segments("A1@@B2@@C3", sep="@@")  # Explicit separator
        ['A1', 'B2', 'C3']
"""

import re
import builtins
from time import time
from typing import Any, Dict, List, Optional, Tuple

from urarovite.core.exceptions import SheetAccessError
from urarovite.utils.drive import duplicate_file_to_drive_folder
from urarovite.utils.google_api_backoff import (
    with_read_backoff,
    with_write_backoff,
    execute_with_backoff,
    READ_CONFIG,
    WRITE_CONFIG,
)

# Regular expressions for parsing
SHEET_ID_RE = re.compile(r"/d/([a-zA-Z0-9-_]+)")
SEGMENT_SEPARATOR = "@@"  # Default separator, can be overridden
COL_RE = r"[A-Z]+"
ROW_RE = r"[0-9]+"


def get_segment_separator() -> str:
    """Get the current segment separator.

    Returns:
        Current segment separator string (default: "@@")
    """
    return SEGMENT_SEPARATOR


def set_segment_separator(separator: str) -> None:
    """Set the global segment separator.

    Args:
        separator: New separator string to use

    Example:
        >>> set_segment_separator(",")
        >>> get_segment_separator()
        ','
    """
    global SEGMENT_SEPARATOR
    SEGMENT_SEPARATOR = separator


def extract_sheet_id(url: str | None) -> Optional[str]:
    """Extract spreadsheet ID from a Google Sheets URL.

    Args:
        url: Google Sheets URL

    Returns:
        Spreadsheet ID if found, None otherwise

    Example:
        >>> extract_sheet_id("https://docs.google.com/spreadsheets/d/1ABC123.../edit")
        "1ABC123..."
    """
    if not url:
        return None
    match = SHEET_ID_RE.search(url)
    return match.group(1) if match else None


def split_segments(ranges_str: str | None, sep: str = None) -> List[str]:
    """Split the verification_field_ranges string into cleaned segments.

    Args:
        ranges_str: String containing range segments separated by separator
        sep: Separator string (default: uses global SEGMENT_SEPARATOR)

    Returns:
        List of cleaned range segments

    Example:
        >>> split_segments("A1@@B2@@C3")
        ['A1', 'B2', 'C3']
        >>> split_segments("A1,B2,C3", sep=",")
        ['A1', 'B2', 'C3']
    """
    if not ranges_str:
        return []
    if sep is None:
        sep = SEGMENT_SEPARATOR
    return [s.strip() for s in ranges_str.split(sep) if s.strip()]


def strip_outer_single_quotes(token: str) -> str:
    """Remove outer single quotes from a token if present.

    Args:
        token: Token that may have outer single quotes

    Returns:
        Token with outer quotes removed
    """
    token = token.strip()
    start_quote = 1 if token.startswith("'") else 0
    end_quote = 1 if token.endswith("'") else 0
    token = token[start_quote : len(token) - end_quote]
    return token


def extract_sheet_and_range(segment: str) -> Tuple[str, Optional[str]]:
    """Split a segment into sheet token and range part.

    Args:
        segment: Range segment (e.g., "Sheet1!A1:B10" or "Sheet1")

    Returns:
        Tuple of (sheet_name, range) where range is None if whole sheet
    """
    if "!" not in segment:
        return segment, None
    sheet, rng = segment.split("!", 1)
    return sheet, rng.strip()


def parse_tab_token(segment: str) -> str:
    """Parse tab name from a range segment.

    Args:
        segment: Range segment

    Returns:
        Clean tab name with quotes removed
    """
    sheet_token, _ = extract_sheet_and_range(segment)
    return strip_outer_single_quotes(sheet_token.strip())


def parse_referenced_tabs(ranges_str: str | None) -> List[str]:
    """Return unique tab names in order of first appearance from ranges string.

    Args:
        ranges_str: String containing range segments

    Returns:
        List of unique tab names in order of appearance
    """
    seen = set()
    ordered: List[str] = []
    for seg in split_segments(ranges_str):
        tab = parse_tab_token(seg)
        if tab not in seen:
            seen.add(tab)
            ordered.append(tab)
    return ordered


# Column letter/index conversions


def col_index_to_letter(idx: int) -> str:
    """Convert column index (0-based) to Excel-style letter.

    Args:
        idx: 0-based column index

    Returns:
        Column letter(s) (e.g., 0 -> "A", 25 -> "Z", 26 -> "AA")
    """
    s = ""
    while idx >= 0:
        s = chr(idx % 26 + 65) + s
        idx = idx // 26 - 1
    return s


def letter_to_col_index(letters: str) -> int:
    """Convert Excel-style column letter(s) to 0-based index.

    Args:
        letters: Column letter(s) (e.g., "A", "Z", "AA")

    Returns:
        0-based column index
    """
    v = 0
    for c in letters:
        v = v * 26 + (ord(c) - 64)
    return v - 1


# Google Sheets data access


@with_read_backoff
def fetch_sheet_tabs(sheets_service: Any, spreadsheet_id: str | None) -> Dict[str, Any]:
    """Fetch tab (sheet) titles using Google Sheets API with exponential backoff.

    Args:
        sheets_service: Google Sheets API service instance
        spreadsheet_id: ID of the spreadsheet

    Returns:
        Dict with keys: accessible, tabs, error
    """
    if not spreadsheet_id:
        return {"accessible": False, "tabs": [], "error": "missing_or_malformed_url"}

    try:
        # Get sheet metadata (list of tabs) with exponential backoff
        def _get_metadata():
            return (
                sheets_service.spreadsheets()
                .get(spreadsheetId=spreadsheet_id, fields="sheets.properties.title")
                .execute()
            )

        sheet_metadata = execute_with_backoff(_get_metadata, config=READ_CONFIG)

        tabs = [
            sheet["properties"]["title"] for sheet in sheet_metadata.get("sheets", [])
        ]
        return {"accessible": True, "tabs": tabs, "error": None}

    except Exception as e:
        error_msg = str(e)
        if "HttpError 403" in error_msg or "HttpError 404" in error_msg:
            return {"accessible": False, "tabs": [], "error": "forbidden_or_not_found"}
        return {
            "accessible": False,
            "tabs": [],
            "error": f"request_exception:{e.__class__.__name__}",
        }


@with_read_backoff
def get_sheet_values(
    sheets_service: Any, spreadsheet_id: str | None, range_name: str
) -> Dict[str, Any]:
    """Get values from a sheet range using Google Sheets API with exponential backoff.

    Args:
        sheets_service: Google Sheets API service instance
        spreadsheet_id: The ID of the spreadsheet
        range_name: The A1 notation range (e.g., 'Sheet1!A1:Z1000')

    Returns:
        Dict with keys: success, values, rows, cols, error
        - rows: number of rows that contain at least one non-empty cell
        - cols: number of columns that contain at least one non-empty cell

    Raises:
        SheetAccessError: If unable to access the sheet
    """
    if not spreadsheet_id:
        return {
            "success": False,
            "values": [],
            "rows": 0,
            "cols": 0,
            "error": "missing_spreadsheet_id",
        }

    try:
        # Execute API call with exponential backoff
        def _get_values():
            return (
                sheets_service.spreadsheets()
                .values()
                .get(
                    spreadsheetId=spreadsheet_id,
                    range=range_name,
                    valueRenderOption="UNFORMATTED_VALUE",
                )
                .execute()
            )

        result = execute_with_backoff(_get_values, config=READ_CONFIG)

        values = result.get("values", [])

        if not values:
            return {"success": True, "values": [], "rows": 0, "cols": 0, "error": None}

        # Find the actual used bounds (last row and column with data)
        used_rows = 0
        used_cols = 0

        for row_idx, row in enumerate(values):
            # Check if this row has any non-empty cells
            has_data = any(cell != "" and cell is not None for cell in row)
            if has_data:
                used_rows = row_idx + 1  # 1-based
                # Update max columns seen
                used_cols = max(used_cols, len(row))

        # Also check for trailing columns in any row that might extend beyond
        if values:
            max_col_in_any_row = max(len(row) for row in values)
            # Find the rightmost column with actual data
            for col_idx in range(max_col_in_any_row - 1, -1, -1):
                has_data_in_col = any(
                    col_idx < len(row)
                    and row[col_idx] != ""
                    and row[col_idx] is not None
                    for row in values
                )
                if has_data_in_col:
                    used_cols = max(used_cols, col_idx + 1)  # 1-based
                    break

        return {
            "success": True,
            "values": values,
            "rows": used_rows,
            "cols": used_cols,
            "error": None,
        }

    except Exception as e:
        error_msg = str(e)
        if "HttpError 403" in error_msg or "HttpError 404" in error_msg:
            return {
                "success": False,
                "values": [],
                "rows": 0,
                "cols": 0,
                "error": "forbidden_or_not_found",
            }
        return {
            "success": False,
            "values": [],
            "rows": 0,
            "cols": 0,
            "error": f"request_exception:{e.__class__.__name__}",
        }


@with_write_backoff
def update_sheet_values(
    sheets_service: Any,
    spreadsheet_id: str,
    range_name: str,
    values: List[List[Any]],
    value_input_option: str = "RAW",
) -> Dict[str, Any]:
    """Update values in a sheet range with exponential backoff.

    Args:
        sheets_service: Google Sheets API service instance
        spreadsheet_id: The ID of the spreadsheet
        range_name: The A1 notation range to update
        values: 2D array of values to write
        value_input_option: How to interpret input data ("RAW" or "USER_ENTERED")

    Returns:
        Dict with update results or error information

    Raises:
        SheetAccessError: If unable to update the sheet
    """
    try:
        # Convert datetime objects to ISO format strings that Google Sheets recognizes as dates
        def convert_datetime_values(data):
            """Recursively convert datetime objects to ISO date strings."""
            import datetime

            if isinstance(data, list):
                return [convert_datetime_values(item) for item in data]
            elif isinstance(data, datetime.datetime):
                # Convert to ISO format that Google Sheets recognizes as datetime
                return data.isoformat()
            elif isinstance(data, datetime.date):
                # Convert to ISO format that Google Sheets recognizes as date
                return data.isoformat()
            elif isinstance(data, datetime.time):
                # Convert to ISO format that Google Sheets recognizes as time
                return data.isoformat()
            else:
                return data

        converted_values = convert_datetime_values(values)

        body = {"values": converted_values}

        # Execute update with exponential backoff
        def _update_values():
            return (
                sheets_service.spreadsheets()
                .values()
                .update(
                    spreadsheetId=spreadsheet_id,
                    range=range_name,
                    valueInputOption=value_input_option,
                    body=body,
                )
                .execute()
            )

        result = execute_with_backoff(_update_values, config=WRITE_CONFIG)

        return {
            "success": True,
            "updated_cells": result.get("updatedCells", 0),
            "updated_rows": result.get("updatedRows", 0),
            "updated_columns": result.get("updatedColumns", 0),
            "error": None,
        }

    except Exception as e:
        error_msg = str(e)
        if "HttpError 403" in error_msg:
            raise SheetAccessError(f"Permission denied: {error_msg}")
        elif "HttpError 404" in error_msg:
            raise SheetAccessError(f"Sheet not found: {error_msg}")
        else:
            raise SheetAccessError(f"Failed to update sheet: {error_msg}")


def _extract_row_bounds_from_a1(a1_range: str) -> tuple[Optional[int], Optional[int]]:
    if not a1_range:
        return None, None
    if "!" in a1_range:
        _, rng = a1_range.split("!", 1)
    else:
        rng = a1_range
    rng = rng.replace(" ", "")
    if ":" in rng:
        start_token, end_token = rng.split(":", 1)
    else:
        start_token, end_token = rng, rng
    start_match = re.search(ROW_RE, start_token)
    end_match = re.search(ROW_RE, end_token)
    start_row = int(start_match.group(0)) if start_match else None
    end_row = int(end_match.group(0)) if end_match else None
    if start_row is not None and end_row is None:
        end_row = start_row
    if start_row is None and end_row is not None:
        start_row = end_row
    return start_row, end_row


def duplicate_sheets_from_sheet_urls_in_range(
    sheets_service: Any | None,
    drive_service: Any | None,
    spreadsheet_url: str | None,
    range: str,
) -> None:
    """Duplicate spreadsheets for each row in a range and write new URLs.

    For each row within the provided A1 range on the specified tab:
    - Column A: source spreadsheet URL to duplicate
    - Column B: destination Google Drive folder URL
    - Column C: populated with the duplicated spreadsheet URL

    The duplicated file name is prefixed with the current Unix time in milliseconds
    to ensure uniqueness.

    Args:
        sheets_service: Google Sheets API service instance. If None, no read/write occurs.
        drive_service: Google Drive API service instance. If None, no read/write occurs.
        spreadsheet_url: URL of the spreadsheet that contains the rows to process.
        range: A1 notation range selecting the rows to process (e.g., "Sheet1!A2:C10").

    Returns:
        None
    """
    spreadsheet_id = extract_sheet_id(spreadsheet_url)
    tab_name = parse_tab_token(range)
    start_row, end_row = _extract_row_bounds_from_a1(range)

    if start_row is None or end_row is None:
        return
    values: List[List[Any]] = []

    if sheets_service is None:
        return {
            "success": False,
            "error": "sheets_service is None",
        }

    if spreadsheet_id is None:
        return {
            "success": False,
            "error": "spreadsheet_id is None",
        }

    result = get_sheet_values(sheets_service, spreadsheet_id, range)
    if result.get("success"):
        values = result.get("values", [])
    else:
        return {
            "success": False,
            "error": result.get("error"),
        }

    for row_index in builtins.range(start_row, end_row + 1):
        local_idx = row_index - start_row
        if 0 <= local_idx < len(values):
            row_values = values[local_idx] or []
            to_be_duplicated_spreadsheet_url = (
                row_values[0] if len(row_values) > 0 else None
            )
            drive_folder_url = row_values[1] if len(row_values) > 1 else None

            unix_time_millis = int(time() * 1000)
            prefix_file_name = f"{unix_time_millis}-"

            drive_copy_result = duplicate_file_to_drive_folder(
                drive_service,
                to_be_duplicated_spreadsheet_url,
                drive_folder_url,
                prefix_file_name,
                sheets_service,
            )

            if drive_copy_result.get("success"):
                new_url = drive_copy_result.get("url")
                if new_url:
                    col_letter = col_index_to_letter(2)
                    target_range = (
                        f"{tab_name}!{col_letter}{row_index}:{col_letter}{row_index}"
                    )
                    try:
                        update_sheet_values(
                            sheets_service,
                            spreadsheet_id,
                            target_range,
                            [[new_url]],
                        )
                    except Exception as e:
                        print(f"Failed to write duplicated URL to sheet: {e}")
            else:
                return {
                    "success": False,
                    "error": drive_copy_result.get("error"),
                    "error_msg": drive_copy_result.get("error_msg"),
                }

    return {
        "success": True,
    }


@with_write_backoff
def rename_spreadsheet_title(
    sheets_service: Any, spreadsheet_id: str, new_title: str
) -> Dict[str, Any]:
    """Rename a spreadsheet title with exponential backoff."""
    try:
        body = {
            "requests": [
                {
                    "updateSpreadsheetProperties": {
                        "properties": {"title": new_title},
                        "fields": "title",
                    }
                }
            ]
        }

        # Execute batch update with exponential backoff
        def _batch_update():
            return (
                sheets_service.spreadsheets()
                .batchUpdate(
                    spreadsheetId=spreadsheet_id,
                    body=body,
                )
                .execute()
            )

        execute_with_backoff(_batch_update, config=WRITE_CONFIG)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


def bulk_rename_spreadsheets_from_range(
    sheets_service: Any,
    template_spreadsheet_url: str | None,
    range: str,
) -> Dict[str, Any]:
    spreadsheet_id = extract_sheet_id(template_spreadsheet_url)
    tab_name = parse_tab_token(range)
    start_row, end_row = _extract_row_bounds_from_a1(range)

    if start_row is None or end_row is None:
        return {"success": False, "error": "invalid_range"}

    if sheets_service is None:
        return {"success": False, "error": "sheets_service is None"}

    if spreadsheet_id is None:
        return {"success": False, "error": "spreadsheet_id is None"}

    read = get_sheet_values(sheets_service, spreadsheet_id, range)
    if not read.get("success"):
        return {"success": False, "error": read.get("error")}

    values: List[List[Any]] = read.get("values", [])
    actions: List[Dict[str, Any]] = []
    successes = 0
    failures = []

    for row_index in builtins.range(start_row, end_row + 1):
        local_idx = row_index - start_row
        row_values = values[local_idx] if 0 <= local_idx < len(values) else []
        target_url = row_values[0] if len(row_values) > 0 else None
        new_title = row_values[1] if len(row_values) > 1 else None

        if not target_url or not new_title:
            actions.append(
                {
                    "row": row_index,
                    "status": "skipped",
                    "reason": "missing_url_or_title",
                }
            )
            continue

        target_id = extract_sheet_id(str(target_url))
        if not target_id:
            action = {
                "row": row_index,
                "status": "failed",
                "reason": "malformed_target_url",
            }
            actions.append(action)
            failures.append(action)
            continue

        rename_result = rename_spreadsheet_title(
            sheets_service, target_id, str(new_title)
        )
        if rename_result.get("success"):
            actions.append(
                {
                    "row": row_index,
                    "status": "renamed",
                    "spreadsheet_id": target_id,
                    "new_title": str(new_title),
                }
            )
            successes += 1
        else:
            action = {
                "row": row_index,
                "status": "failed",
                "spreadsheet_id": target_id,
                "new_title": str(new_title),
                "error": rename_result.get("error"),
            }
            actions.append(action)
            failures.append(action)

    return {
        "success": len(failures) == 0,
        "tab": tab_name,
        "start_row": start_row,
        "end_row": end_row,
        "actions": actions,
        "renamed": successes,
        "failures": failures,
    }


@with_read_backoff
def fetch_workbook_with_formulas(
    sheets_service: Any, spreadsheet_id: str
) -> Dict[str, Any]:
    """Fetch workbook grid including formulas and effective values with exponential backoff.

    Args:
        sheets_service: Google Sheets API service instance
        spreadsheet_id: The ID of the spreadsheet

    Returns:
        Dict with keys: properties, sheets (with grid data)
    """

    def _get_workbook():
        return (
            sheets_service.spreadsheets()
            .get(
                spreadsheetId=spreadsheet_id,
                includeGridData=True,
                fields=(
                    "properties.title,"
                    "sheets(properties.title,"
                    "data.rowData.values.userEnteredValue.formulaValue,"
                    "data.rowData.values.formattedValue,"
                    "data.rowData.values.effectiveValue)"
                ),
            )
            .execute()
        )

    return execute_with_backoff(_get_workbook, config=READ_CONFIG)


@with_read_backoff
def get_sheet_data_with_hyperlinks(
    sheets_service: Any, spreadsheet_id: str, sheet_name: str, sheet_gid: int
) -> list[list[Any]]:
    """
    Fetches sheet data from a specific sheet, resolving hyperlinks to their URLs.

    Args:
        sheets_service: Google Sheets API service instance.
        spreadsheet_id: The ID of the spreadsheet.
        sheet_name: The name of the sheet (for fallback).
        sheet_gid: The grid ID (gid) of the sheet to fetch.

    Returns:
        A list of lists representing the sheet data.
    """
    try:
        workbook_data = (
            sheets_service.spreadsheets()
            .get(
                spreadsheetId=spreadsheet_id,
                fields="sheets(properties.sheetId,data.rowData.values(formattedValue,hyperlink))",
            )
            .execute()
        )

        sheet_data = None
        for s in workbook_data.get("sheets", []):
            if s.get("properties", {}).get("sheetId") == sheet_gid:
                sheet_data = s
                break

        if not sheet_data:
            return []

        rows = []
        grid_data = sheet_data.get("data", [{}])[0]
        for row_data in grid_data.get("rowData", []):
            row_values = []
            if "values" in row_data:
                for cell in row_data.get("values", []):
                    if "hyperlink" in cell:
                        row_values.append(cell["hyperlink"])
                    else:
                        row_values.append(cell.get("formattedValue", ""))
            rows.append(row_values)

        if rows:
            max_len = max((len(row) for row in rows), default=0)
            for row in rows:
                row.extend([""] * (max_len - len(row)))

        return rows

    except Exception as e:
        result = get_sheet_values(sheets_service, spreadsheet_id, sheet_name)
        if result["success"]:
            return result.get("values", [])
        else:
            raise SheetAccessError(
                f"Failed to get sheet values for {sheet_name}: {result['error']}"
            ) from e


def create_new_spreadsheet_in_folder(
    gspread_client: Any, folder_id: str, spreadsheet_name: str
) -> Any:
    """Create a new Google Sheets document directly in a Shared Drive folder.

    Args:
        gspread_client: gspread client instance
        folder_id: Google Drive folder ID where the spreadsheet should be created
        spreadsheet_name: Name for the new spreadsheet

    Returns:
        gspread Spreadsheet object or None if creation failed
    """
    try:
        # CRITICAL: Create spreadsheet directly in the target folder using Drive API
        # This bypasses gspread.create() which doesn't support supportsAllDrives

        # Get Drive service from gspread client credentials
        # gspread client stores credentials at http_client.auth
        from googleapiclient.discovery import build

        # Get credentials from gspread client
        credentials = gspread_client.http_client.auth
        drive_service = build("drive", "v3", credentials=credentials)

        # Create Google Sheets directly in the target folder
        file_metadata = {
            "name": spreadsheet_name,
            "parents": [folder_id],  # Create directly in target folder
            "mimeType": "application/vnd.google-apps.spreadsheet",
        }

        # Create file with Shared Drive support
        created_file = (
            drive_service.files()
            .create(
                body=file_metadata,
                supportsAllDrives=True,  # CRITICAL: Support for Shared Drives
            )
            .execute()
        )

        # Return gspread Spreadsheet object
        spreadsheet = gspread_client.open_by_key(created_file["id"])
        return spreadsheet

    except Exception as e:
        import logging

        logging.error(f"Failed to create spreadsheet in folder {folder_id}: {str(e)}")
        return None
