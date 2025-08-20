"""
Open-Ended Range Validator.

This validator detects unbounded/unstable A1 notations in verification_field_ranges
that can cause flaky verification due to sensitivity to trailing empties and layout changes.

Goal:
Identify open-ended range patterns that should be bounded for stable verification:
- Whole columns: A:A, A:B, C:Z
- Whole rows: 3:3, 10:12
- Half-bounded columns: A1:A, A1:Z (missing terminating row number)

Why:
Open ranges are sensitive to trailing empties; layout changes create spurious diffs,
making verification unstable. This validator helps identify and suggest fixes.
"""

from __future__ import annotations
import re
from typing import List, Dict, Any, Tuple, Union
from pathlib import Path
import pandas as pd

from urarovite.validators.base import BaseValidator, ValidationResult
from urarovite.core.exceptions import ValidationError
from urarovite.core.spreadsheet import SpreadsheetInterface
from urarovite.utils.sheets import (
    extract_sheet_id,
    split_segments,
    extract_sheet_and_range,
    col_index_to_letter,
    strip_outer_single_quotes,
    get_sheet_values,
)


class OpenEndedRangesValidator(BaseValidator):
    """Validator that detects open-ended ranges in verification field ranges."""

    def __init__(self) -> None:
        super().__init__(
            validator_id="open_ended_ranges",
            name="Open-Ended Ranges Detection",
            description=(
                "Detects unbounded A1 notations in verification ranges that "
                "can cause flaky verification (whole columns, rows, half-bounded ranges)"
            ),
        )

    # Regular expression patterns for range detection
    COL_RE = r"[A-Z]+"
    ROW_RE = r"[0-9]+"

    WHOLE_COL_PATTERN = re.compile(rf"^{COL_RE}:{COL_RE}$")  # A:A, A:B
    WHOLE_ROW_PATTERN = re.compile(rf"^{ROW_RE}:{ROW_RE}$")  # 3:3, 3:10
    HALF_BOUNDED_COL_PATTERN = re.compile(
        rf"^{COL_RE}{ROW_RE}:{COL_RE}$"
    )  # A1:A, B10:C

    DEFAULT_TAB_SCAN_RANGE = "A1:ZZ1000"

    def _is_open_ended(self, range_part: str) -> Tuple[str | None, bool]:
        """
        Classify range_part and return (reason, is_open_ended).

        We consider fully bounded if both sides have column+row tokens (e.g. A1:B20)
        or single-cell references (A1). Everything else in patterns listed is open-ended.
        """
        if not range_part:
            return None, False

        # Single cell like A1 or B20
        if re.fullmatch(rf"{self.COL_RE}{self.ROW_RE}", range_part):
            return None, False

        # Whole column or multi-column entire columns
        if self.WHOLE_COL_PATTERN.match(range_part):
            return "whole_column", True

        # Whole row(s)
        if self.WHOLE_ROW_PATTERN.match(range_part):
            return "whole_row", True

        # Half-bounded column (A1:A or A1:Z) -> second side missing row digits
        if ":" in range_part:
            left, right = range_part.split(":", 1)
            left_col_row = (
                re.fullmatch(rf"{self.COL_RE}{self.ROW_RE}", left) is not None
            )
            right_col_only = re.fullmatch(rf"{self.COL_RE}", right) is not None
            # Fully bounded check: both sides col+row
            both_col_row = (
                left_col_row
                and re.fullmatch(rf"{self.COL_RE}{self.ROW_RE}", right) is not None
            )
            if both_col_row:
                return None, False  # bounded
            if left_col_row and right_col_only:
                return "half_bounded_column", True
            # If left is col only and right col only (A:B) -> treat as whole columns
            if re.fullmatch(rf"{self.COL_RE}", left) and re.fullmatch(
                rf"{self.COL_RE}", right
            ):
                return "whole_column", True
            # If left is row only and right row only -> whole row(s)
            if re.fullmatch(rf"{self.ROW_RE}", left) and re.fullmatch(
                rf"{self.ROW_RE}", right
            ):
                return "whole_row", True

        return None, False

    def _suggest_data_bound(
        self, sheet: str, range_part: str, reason: str, rows: int, cols: int
    ) -> str:
        """Generate a bounded range suggestion based on actual data bounds."""
        sheet_prefix = f"{sheet}!" if sheet else ""
        if rows <= 0 or cols <= 0:
            return f"{sheet_prefix}{range_part}"  # fallback

        last_col_letter = col_index_to_letter(cols - 1)

        if reason == "whole_column":
            parts = range_part.split(":")
            start_col = parts[0]
            end_col = parts[-1]
            return f"{sheet_prefix}{start_col}1:{end_col}{rows}"
        elif reason == "half_bounded_column":
            left, right = range_part.split(":", 1)
            # left like A1 or B10; keep starting row as-is
            return f"{sheet_prefix}{left}:{right}{rows}"
        elif reason == "whole_row":
            rows_part = range_part.split(":")
            start_row = rows_part[0]
            end_row = rows_part[-1]
            return f"{sheet_prefix}A{start_row}:{last_col_letter}{end_row}"

        return f"{sheet_prefix}{range_part}"

    def _get_tab_bounds(self, spreadsheet_id: str | None, tab: str) -> Tuple[int, int]:
        """
        Return (used_rows, used_cols) for a tab using OAuth authentication.

        used_rows: highest 1-based row index containing any non-empty cell (0 if none)
        used_cols: highest 1-based column index containing any non-empty cell (0 if none)
        Returns (0,0) on failure or if spreadsheet_id missing.
        """
        if not spreadsheet_id:
            return 0, 0

        # Clean tab name
        clean_tab = strip_outer_single_quotes(tab) if "'" in tab else tab

        # Try to get a reasonable range to scan for data bounds
        range_name = f"'{clean_tab}'!{self.DEFAULT_TAB_SCAN_RANGE}"

        try:
            result = get_sheet_values(spreadsheet_id, range_name)
            if not result["success"]:
                return 0, 0

            return result["rows"], result["cols"]

        except Exception:
            return 0, 0

    def validate(
        self,
        spreadsheet_source: Union[str, Path, SpreadsheetInterface],
        mode: str,
        auth_credentials: Dict[str, Any] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Execute open-ended range detection.

        Args:
            spreadsheet_source: Either a Google Sheets URL, Excel file path,
                or SpreadsheetInterface
            mode: Either "fix" (not applicable) or "flag" (report only)
            auth_credentials: Authentication credentials (only needed for tab bounds)
            **kwargs: Must contain 'row' with pandas Series or dict containing the data

        Returns:
            Dict with validation results
        """
        # This validator can work without spreadsheet access for basic range parsing
        # It only needs spreadsheet access for getting tab bounds, which we can mock
        result = ValidationResult()

        try:
            self._perform_validation_logic(result, **kwargs)
        except Exception as e:
            result.add_error(f"Unexpected error: {str(e)}")
            if not result.automated_log:
                result.set_automated_log(f"Unexpected error: {str(e)}")

        # Ensure automated log is set
        self._set_default_log_if_empty(result)
        return result.to_dict()

    def _perform_validation_logic(self, result: ValidationResult, **kwargs) -> None:
        # Extract parameters
        row = kwargs.get("row")
        if row is None:
            # Return empty result if no row data provided
            result.details["open_ended_count"] = 0
            result.details["open_ended"] = []
            result.set_automated_log("No flags found")
            return

        field = kwargs.get("field", "verification_field_ranges")
        input_col = kwargs.get("input_col", "input_sheet_url")
        output_col = kwargs.get("output_col", "example_output_sheet_url")

        # Extract data from row
        ranges_str = row.get(field, "")
        separator = kwargs.get("separator", None)  # Allow custom separator
        segments = split_segments(ranges_str, sep=separator)
        open_ended: List[Dict[str, Any]] = []

        input_sid = extract_sheet_id(row.get(input_col))
        output_sid = extract_sheet_id(row.get(output_col))

        # Cache tab bounds to avoid repeated API calls
        cache_input: Dict[str, Tuple[int, int]] = {}
        cache_output: Dict[str, Tuple[int, int]] = {}

        for seg in segments:
            sheet, range_part = extract_sheet_and_range(seg)
            if not range_part:
                continue  # whole-sheet reference

            reason, flagged = self._is_open_ended(range_part)
            if not (flagged and reason):
                continue

            tab_clean = sheet.strip()
            if tab_clean.startswith("'") and tab_clean.endswith("'"):
                tab_clean = strip_outer_single_quotes(tab_clean)

            # Get bounds for both input and output sheets
            if tab_clean not in cache_input:
                cache_input[tab_clean] = self._get_tab_bounds(input_sid, tab_clean)
            if tab_clean not in cache_output:
                cache_output[tab_clean] = self._get_tab_bounds(output_sid, tab_clean)

            in_rows, in_cols = cache_input[tab_clean]
            out_rows, out_cols = cache_output[tab_clean]

            # Determine best bounds to use for suggestion
            candidates_rows = [v for v in (in_rows, out_rows) if v > 0]
            candidates_cols = [v for v in (in_cols, out_cols) if v > 0]

            used_rows = min(candidates_rows) if candidates_rows else 0
            used_cols = min(candidates_cols) if candidates_cols else 0

            # Generate suggestion based on available data
            if used_rows > 0 and used_cols > 0:
                suggestion = self._suggest_data_bound(
                    sheet, range_part, reason, used_rows, used_cols
                )
                suggestion_source = "data"
            elif used_rows > 0 and reason in ("whole_column", "half_bounded_column"):
                # Have row info but not column info
                suggestion = self._suggest_data_bound(
                    sheet, range_part, reason, used_rows, max(in_cols, out_cols) or 26
                )
                suggestion_source = "partial"
            elif used_cols > 0 and reason == "whole_row":
                suggestion = self._suggest_data_bound(
                    sheet, range_part, reason, max(in_rows, out_rows) or 100, used_cols
                )
                suggestion_source = "partial"
            else:
                # Fallback: use reasonable defaults
                default_rows = 100
                default_cols = 26
                suggestion = self._suggest_data_bound(
                    sheet, range_part, reason, default_rows, default_cols
                )
                suggestion_source = "default"

            result.add_detailed_issue(
                sheet_name=sheet,
                cell=range_part,
                message=f"Open-ended range detected (reason: {reason})",
                value=seg,
            )

            entry: Dict[str, Any] = {
                "segment": seg,
                "range_part": range_part,
                "reason": reason,
                "suggested": suggestion,
                "suggestion_source": suggestion_source,
                "tab_bounds": {
                    "input": {"rows": in_rows, "cols": in_cols},
                    "output": {"rows": out_rows, "cols": out_cols},
                    "used_rows": used_rows,
                    "used_cols": used_cols,
                },
            }
            open_ended.append(entry)

        result.details["total_segments"] = len(segments)
        result.details["open_ended"] = open_ended
        result.details["open_ended_count"] = len(open_ended)
        result.details["original"] = ranges_str

        if open_ended:
            result.set_automated_log(
                f"Open-ended ranges found: {len(open_ended)} ranges"
            )
        else:
            result.set_automated_log("No flags found")


# Convenience function for backward compatibility
def run(
    row: Union[Dict[str, Any], "pd.Series"],
    field: str = "verification_field_ranges",
    input_col: str = "input_sheet_url",
    output_col: str = "example_output_sheet_url",
) -> Dict[str, Any]:
    """
    Execute open-ended range detection.
    This function provides backward compatibility with the original checker4 interface.
    """
    validator = OpenEndedRangesValidator()

    try:
        # Use dummy spreadsheet source since this validator works with row data
        dummy_source = "https://docs.google.com/spreadsheets/d/dummy/edit"

        return validator.validate(
            spreadsheet_source=dummy_source,
            mode="flag",
            auth_credentials=None,  # Not needed for this validator's logic
            row=row,
            field=field,
            input_col=input_col,
            output_col=output_col,
        )
    except Exception as e:
        # Return error in ValidationResult format
        result = ValidationResult()
        result.add_error(f"validation_error: {str(e)}")
        result.details["total_segments"] = 0
        result.details["open_ended"] = []
        result.details["open_ended_count"] = 0
        result.details["original"] = ""
        result.set_automated_log("No flags found")
        return result.to_dict()
