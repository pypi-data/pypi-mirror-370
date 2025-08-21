"""Empty and invalid ranges validator for Google Sheets.

This validator checks whether A1 ranges in Google Sheets are valid and non-empty
using the Google Sheets API.
"""

import re
from typing import Any, Dict, List, Tuple, Union
from pathlib import Path

from urarovite.validators.base import BaseValidator, ValidationResult
from urarovite.core.exceptions import ValidationError
from urarovite.core.spreadsheet import SpreadsheetInterface
from urarovite.utils.sheets import extract_sheet_id, get_sheet_values


class EmptyInvalidRangesValidator(BaseValidator):
    """Validator for checking empty and invalid ranges in Google Sheets."""

    # Regex patterns for A1 geometry sanity checks
    _A1_RECT_RE = re.compile(r"^([A-Za-z]+)(\d+):([A-Za-z]+)(\d+)$")
    _A1_CELL_RE = re.compile(r"^([A-Za-z]+)(\d+)$")
    _A1_COL_RE = re.compile(r"^([A-Za-z]+):([A-Za-z]+)$")
    _A1_ROW_RE = re.compile(r"^(\d+):(\d+)$")

    def __init__(self) -> None:
        super().__init__(
            validator_id="empty_invalid_ranges",
            name="Check Empty and Invalid Ranges",
            description="Validates that A1 ranges are valid and contain non-empty data",
        )

    def validate(
        self,
        spreadsheet_source: Union[str, Path, SpreadsheetInterface],
        mode: str,
        auth_credentials: Dict[str, Any] = None,
        range_columns: List[int] = None,
        url_columns: List[int] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Validate ranges for emptiness and invalidity.

        Args:
            spreadsheet_source: Either a Google Sheets URL, Excel file path,
                or SpreadsheetInterface
            mode: Either "fix" (not applicable) or "flag" (report only)
            auth_credentials: Authentication credentials (required for Google Sheets)
            range_columns: List of 1-based column indices containing A1 ranges
            url_columns: List of 1-based column indices containing spreadsheet URLs

        Returns:
            Dict with validation results
        """

        def validation_logic(
            spreadsheet: SpreadsheetInterface, result: ValidationResult, **kwargs
        ) -> None:
            # Get all sheet data
            data, sheet_name = self._get_all_sheet_data(spreadsheet)

            if not data:
                result.add_error("Sheet is empty - no data to validate")
                result.details["valid_ranges"] = 0
                result.details["invalid_ranges"] = []
                result.set_automated_log("Sheet is empty - no data to validate")
                return

            # Auto-detect range and URL columns if not specified
            detected_range_columns = range_columns
            detected_url_columns = url_columns

            if detected_range_columns is None:
                detected_range_columns = self._detect_range_columns(data)
            if detected_url_columns is None:
                detected_url_columns = self._detect_url_columns(data)

            if not detected_range_columns or not detected_url_columns:
                result.details["message"] = "No range or URL columns found in data"
                result.details["valid_ranges"] = 0
                result.details["invalid_ranges"] = []
                result.set_automated_log("No range or URL columns detected")
                return

            # Create sheets service for range validation
            try:
                sheets_service = self._create_sheets_service(auth_credentials)
            except ValidationError as e:
                result.add_error(str(e))
                return

            # Check each range in the specified columns
            for row_idx, row in enumerate(data):
                if row_idx == 0:  # Skip header row
                    continue

                # Get range and URL from the row
                range_value = None
                url_value = None
                range_col_idx = -1

                for col_idx in detected_range_columns:
                    if col_idx <= len(row) and row[col_idx - 1]:
                        range_value = str(row[col_idx - 1]).strip()
                        range_col_idx = col_idx - 1
                        break

                for col_idx in detected_url_columns:
                    if col_idx <= len(row) and row[col_idx - 1]:
                        url_value = str(row[col_idx - 1]).strip()
                        break

                if range_value and url_value:
                    validation_result = self._validate_sheet_range(
                        sheets_service, range_value, url_value
                    )

                    if not validation_result[0]:  # Not valid
                        cell_ref = self._generate_cell_reference(
                            row_idx, range_col_idx, sheet_name
                        )
                        result.add_detailed_issue(
                            sheet_name=sheet_name,
                            cell=cell_ref,
                            message=validation_result[1],
                            value=range_value,
                        )

            # Record results
            if result.flags_found > 0:
                result.set_automated_log(
                    f"Found {result.flags_found} empty or invalid ranges."
                )
            else:
                result.set_automated_log("All ranges are valid and non-empty.")

        return self._execute_validation(
            validation_logic, spreadsheet_source, auth_credentials, **kwargs
        )

    def _col_to_num(self, col: str) -> int:
        """Convert column letter(s) to number."""
        n = 0
        for ch in col.upper():
            if not ("A" <= ch <= "Z"):
                return -1
            n = n * 26 + (ord(ch) - ord("A") + 1)
        return n

    def _zero_sized(self, a1: str) -> bool:
        """Detect 0-sized/invalid geometry from common A1 forms."""
        m = self._A1_RECT_RE.match(a1)
        if m:
            c1, r1, c2, r2 = m.groups()
            c1n, c2n = self._col_to_num(c1), self._col_to_num(c2)
            r1n, r2n = int(r1), int(r2)
            return (
                c1n <= 0
                or c2n <= 0
                or r1n <= 0
                or r2n <= 0
                or (c2n - c1n + 1) <= 0
                or (r2n - r1n + 1) <= 0
            )

        m = self._A1_COL_RE.match(a1)
        if m:
            c1, c2 = m.groups()
            c1n, c2n = self._col_to_num(c1), self._col_to_num(c2)
            return c1n <= 0 or c2n <= 0 or (c2n - c1n + 1) <= 0

        m = self._A1_ROW_RE.match(a1)
        if m:
            r1, r2 = map(int, m.groups())
            return r1 <= 0 or r2 <= 0 or (r2 - r1 + 1) <= 0

        # Single-cell or open-ended ranges (A1:B, A:A, 1:), let API decide.
        return False

    def _validate_sheet_range(
        self, sheets_service: Any, a1_range: str, spreadsheet_url: str
    ) -> Tuple[bool, str]:
        """Validate that `a1_range` exists in the Google Sheet and is NOT empty."""
        # URL sanity
        spreadsheet_id = extract_sheet_id(spreadsheet_url)
        if not spreadsheet_id:
            return (False, "Invalid spreadsheet URL — manual fix required")

        # Range sanity (basic)
        if not isinstance(a1_range, str) or not a1_range.strip():
            return (False, "Range is missing — manual fix required")
        a1_range = a1_range.strip()

        # For geometry checks, isolate the portion after "!" if present.
        pure_range = a1_range.split("!", 1)[1].strip() if "!" in a1_range else a1_range
        if self._zero_sized(pure_range):
            return (False, "Range is invalid or 0-sized — manual fix required")

        # Use the existing utility to get sheet values
        try:
            result = get_sheet_values(sheets_service, spreadsheet_id, a1_range)

            if not result["success"]:
                error = result.get("error", "unknown")
                if error == "forbidden_or_not_found":
                    return (
                        False,
                        "No access to the spreadsheet or sheet not found — manual fix required",
                    )
                elif "request_exception" in error:
                    return (
                        False,
                        f"Google Sheets API error: {error} — manual fix required",
                    )
                else:
                    return (
                        False,
                        f"Failed to access range: {error} — manual fix required",
                    )

            values = result.get("values", [])
            # Check if any cell contains non-empty data
            non_empty = any(
                (cell is not None) and (str(cell).strip() != "")
                for row in values
                for cell in row
            )

            if not non_empty:
                return (False, "Range is empty — manual fix required")

            return (True, "Range is valid and not empty")

        except Exception as e:
            return (
                False,
                f"Unexpected error: {e.__class__.__name__} — manual fix required",
            )

    def _detect_range_columns(self, data: List[List[Any]]) -> List[int]:
        """Auto-detect columns containing A1 ranges."""
        range_columns = []

        if not data:
            return range_columns

        # Check first few rows for A1 range patterns
        sample_rows = data[: min(10, len(data))]

        for col_idx in range(len(data[0]) if data[0] else 0):
            contains_ranges = False

            for row in sample_rows:
                if col_idx < len(row) and row[col_idx]:
                    cell_value = str(row[col_idx]).strip()
                    # Look for A1 notation patterns
                    if "!" in cell_value and (
                        self._A1_RECT_RE.search(cell_value.split("!")[-1])
                        or self._A1_CELL_RE.search(cell_value.split("!")[-1])
                        or self._A1_COL_RE.search(cell_value.split("!")[-1])
                        or self._A1_ROW_RE.search(cell_value.split("!")[-1])
                    ):
                        contains_ranges = True
                        break

            if contains_ranges:
                range_columns.append(col_idx + 1)  # Convert to 1-based

        return range_columns

    def _detect_url_columns(self, data: List[List[Any]]) -> List[int]:
        """Auto-detect columns containing Google Sheets URLs."""
        url_columns = []

        if not data:
            return url_columns

        # Check first few rows for URLs
        sample_rows = data[: min(10, len(data))]

        for col_idx in range(len(data[0]) if data[0] else 0):
            contains_urls = False

            for row in sample_rows:
                if col_idx < len(row) and row[col_idx]:
                    cell_value = str(row[col_idx])
                    # Use the utility function to check if it contains a valid sheet ID
                    if extract_sheet_id(cell_value) is not None:
                        contains_urls = True
                        break

            if contains_urls:
                url_columns.append(col_idx + 1)  # Convert to 1-based

        return url_columns
