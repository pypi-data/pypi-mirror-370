"""
Validator: Different Within Ranges Validator.

This validator ensures that input and example output spreadsheets are DIFFERENT
within EVERY cell listed in verification_field_ranges.

Goal:
Assert that EVERY verification range differs between input and output.

Why:
Prompts require specific edits in verification ranges; identical content
in those cells indicates the task wasn't completed.
"""

from __future__ import annotations
import re
from typing import Dict, List, Tuple, Any
from typing import Union

try:
    import pandas as pd
except ImportError:
    pd = None

from urarovite.validators.base import BaseValidator, ValidationResult
from urarovite.core.exceptions import ValidationError
from urarovite.utils.sheets import (
    split_segments,
    extract_sheet_id,
    strip_outer_single_quotes,
)
from urarovite.auth.google_sheets import create_sheets_service_from_encoded_creds


class DifferentWithinRangesValidator(BaseValidator):
    """Validator that checks input vs output spreadsheets differ
    within all specified verification ranges.
    """

    def __init__(self) -> None:
        super().__init__(
            validator_id="different_within_ranges",
            name="Different Within Ranges Validator",
            description="Ensures input and output spreadsheets are "
            "different within all specified verification ranges",
        )

    # ---------- A1 helpers ----------
    _A1_RNG = re.compile(
        r"^'?(?P<tab>[^'!]*)'?!?(?P<start>[A-Z]+[0-9]+)"
        r"(:(?P<end>[A-Z]+[0-9]+))?$"
    )

    @staticmethod
    def _col_to_n(col: str) -> int:
        """Convert column letter to number (A=1, B=2, etc.)."""
        n = 0
        for ch in col:
            n = n * 26 + (ord(ch) - 64)
        return n

    @staticmethod
    def _n_to_col(n: int) -> str:
        """Convert number to column letter (1=A, 2=B, etc.)."""
        s = ""
        while n:
            n, r = divmod(n - 1, 26)
            s = chr(65 + r) + s
        return s or "A"

    @staticmethod
    def _a1_to_rc(a1: str) -> Tuple[int, int]:
        """Convert A1 notation to row, col indices (0-based)."""
        m = re.match(r"^([A-Z]+)(\d+)$", a1)
        if not m:
            raise ValueError(f"Bad A1 token: {a1}")
        col_n = DifferentWithinRangesValidator._col_to_n(m.group(1))
        return int(m.group(2)) - 1, col_n - 1

    def _expand_a1_range(self, seg: str) -> Tuple[str, Tuple[int, int, int, int]]:
        """
        Accepts "'Tab'!A1:B9" or "A1:B9" (tab may be empty).
        Returns (tab, (r1,c1,r2,c2)) all zero-based inclusive.
        """
        s = seg.strip()
        has_tab = "!" in s
        m = self._A1_RNG.match(s if has_tab else f"X!{s}")
        if not m:
            raise ValueError(f"Bad A1 range: {seg}")
        tab = (m.group("tab") or "").strip() if has_tab else ""
        r1, c1 = self._a1_to_rc(m.group("start"))
        if m.group("end"):
            r2, c2 = self._a1_to_rc(m.group("end"))
        else:
            r2, c2 = r1, c1
        if r1 > r2:
            r1, r2 = r2, r1
        if c1 > c2:
            c1, c2 = c2, c1
        return tab.strip("'"), (r1, c1, r2, c2)

    def _a1_dims(self, a1: str) -> Tuple[int, int]:
        """Return (height, width) implied by the A1 range."""
        tab, (r1, c1, r2, c2) = self._expand_a1_range(a1)
        return r2 - r1 + 1, c2 - c1 + 1

    def _extract_tab(self, a1: str) -> str:
        """Extract tab name from A1 range."""
        s = a1.strip()
        if "!" in s:
            m = self._A1_RNG.match(s)
            if m:
                tab = (m.group("tab") or "").strip()
                return (
                    strip_outer_single_quotes(tab)
                    if tab.startswith("'") and tab.endswith("'")
                    else tab
                )
        return ""

    def _range_part(self, a1: str) -> str:
        """Extract the range part (without tab) from A1 range."""
        return a1.split("!", 1)[1] if "!" in a1 else a1

    @staticmethod
    def _a1_from_rc(r0: int, c0: int) -> str:
        """Convert 0-based row, col to A1 notation."""
        col_letter = DifferentWithinRangesValidator._n_to_col(c0 + 1)
        return f"{col_letter}{r0 + 1}"

    def _pad(self, mat: List[List[Any]] | None, h: int, w: int) -> List[List[Any]]:
        """Make a dense h×w matrix; API may drop blank rows/cols."""
        mat = mat or []
        out = [[""] * w for _ in range(h)]
        for r in range(min(h, len(mat))):
            row = mat[r] or []
            for c in range(min(w, len(row))):
                out[r][c] = row[c]
        return out

    def _get_sheet_values_batch(
        self, sheets_service: Any, spreadsheet_id: str, ranges: List[str]
    ) -> List[List[List[Any]]]:
        """Get values from multiple ranges in a single batch request."""
        try:
            resp = (
                sheets_service.spreadsheets()
                .values()
                .batchGet(
                    spreadsheetId=spreadsheet_id,
                    ranges=ranges,
                    valueRenderOption="UNFORMATTED_VALUE",
                    dateTimeRenderOption="FORMATTED_STRING",
                )
                .execute()
            )
            return [vr.get("values", []) for vr in resp.get("valueRanges", [])]
        except Exception as e:
            raise ValidationError(f"Failed to fetch batch sheet values: {str(e)}")

    def validate(
        self,
        spreadsheet_source: Union[str, Any],
        mode: str,
        auth_credentials: Dict[str, Any] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Execute the validation check.

        Args:
            spreadsheet_source: Not used - sheet URLs are extracted from
                row data
            mode: Either "fix" (not applicable) or "flag" (report only)
            auth_credentials: Authentication credentials for Google Sheets
                access
            **kwargs: Must contain 'row' with pandas Series containing:
                - verification_field_ranges: ranges to check
                - input_sheet_url: input sheet URL
                - example_output_sheet_url: output sheet URL

        Returns:
            Dict with validation results

        Raises:
            ValidationError: If validation fails
        """
        # Extract required parameters
        row = kwargs.get("row")
        if row is None:
            # Return empty result if no row data provided
            result = ValidationResult()
            result.set_automated_log("No flags found")
            return result.to_dict()

        field = kwargs.get("field", "verification_field_ranges")
        input_col = kwargs.get("input_col", "input_sheet_url")
        output_col = kwargs.get("output_col", "example_output_sheet_url")
        max_report_per_segment = kwargs.get("max_report_per_segment", 100)

        ranges_str = (row.get(field) or "").strip()
        separator = kwargs.get("separator", None)  # Allow custom separator
        segments = split_segments(ranges_str, sep=separator)

        input_sid = extract_sheet_id(row.get(input_col))
        output_sid = extract_sheet_id(row.get(output_col))

        if not input_sid or not output_sid:
            result = ValidationResult()
            result.add_error("Missing input/output spreadsheet IDs")
            result.details["total_segments"] = len(segments)
            result.details["total_diff_cells"] = 0
            result.details["segments"] = []
            result.details["original"] = ranges_str
            result.set_automated_log("No flags found")
            return result.to_dict()

        try:
            # Create sheets service from auth credentials
            sheets_service = None
            if auth_credentials and "auth_secret" in auth_credentials:
                sheets_service = create_sheets_service_from_encoded_creds(
                    auth_credentials["auth_secret"]
                )

            if not sheets_service:
                result = ValidationResult()
                result.add_error("No valid authentication credentials provided")
                result.details["total_segments"] = len(segments)
                result.details["total_diff_cells"] = 0
                result.details["segments"] = []
                result.details["original"] = ranges_str
                result.set_automated_log("No flags found")
                return result.to_dict()

            # Fetch all segments at once from both sheets
            left_vals = self._get_sheet_values_batch(
                sheets_service, input_sid, segments
            )
            right_vals = self._get_sheet_values_batch(
                sheets_service, output_sid, segments
            )
            segments_out: List[Dict[str, Any]] = []
            total_diff = 0
            all_differ = True
            identical_segments = []

            for a1, L_raw, R_raw in zip(segments, left_vals, right_vals):
                h, w = self._a1_dims(a1)
                L = self._pad(L_raw, h, w)
                R = self._pad(R_raw, h, w)

                # Count diffs within this segment
                dc = 0
                diffs_sample: List[Dict[str, Any]] = []
                for r in range(h):
                    for c in range(w):
                        if L[r][c] != R[r][c]:
                            dc += 1
                            if len(diffs_sample) < max_report_per_segment:
                                diffs_sample.append(
                                    {
                                        "range_row": r + 1,
                                        "range_col": c + 1,
                                        "a1": self._a1_from_rc(r, c),
                                        "input": L[r][c],
                                        "output": R[r][c],
                                    }
                                )

                equal = dc == 0
                if equal:
                    all_differ = False
                    identical_segments.append(a1)
                total_diff += dc

                segments_out.append(
                    {
                        "segment": a1,
                        "tab": self._extract_tab(a1),
                        "range_part": self._range_part(a1),
                        "diff_count": dc,
                        "identical": equal,
                        "diffs": diffs_sample,
                    }
                )

            # Prepare result using ValidationResult
            result = ValidationResult()

            if not all_differ:
                # Count how many segments are identical (this is the issue)
                identical_count = len(identical_segments)
                result.add_issue(identical_count)
                result.set_automated_log(
                    f"Found {identical_count} identical segments that should differ"
                )
            else:
                result.set_automated_log("All verification ranges differ as expected")

            # Store detailed results
            result.details["total_segments"] = len(segments)
            result.details["total_diff_cells"] = total_diff
            result.details["segments"] = segments_out
            result.details["original"] = ranges_str
            result.details["identical_segments"] = identical_segments

            return result.to_dict()

        except Exception as e:
            error_msg = f"Failed to validate different within ranges: {str(e)}"
            raise ValidationError(error_msg)


# Convenience function for backward compatibility
def run(
    row: Union[Dict[str, Any], "pd.Series"],
    field: str = "verification_field_ranges",
    input_col: str = "input_sheet_url",
    output_col: str = "example_output_sheet_url",
    max_report_per_segment: int = 100,
) -> Dict[str, Any]:
    """
    Execute comparison: input vs output must be different WITHIN
    verification ranges.
    This function provides backward compatibility with the original
    checker interface.
    """
    validator = DifferentWithinRangesValidator()
    return validator.validate(
        spreadsheet_source="",  # Not used by this validator
        mode="flag",
        auth_credentials=None,  # No auth for backward compatibility
        row=row,
        field=field,
        input_col=input_col,
        output_col=output_col,
        max_report_per_segment=max_report_per_segment,
    )
