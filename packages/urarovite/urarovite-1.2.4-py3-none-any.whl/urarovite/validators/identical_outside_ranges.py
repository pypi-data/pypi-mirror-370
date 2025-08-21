"""
Validator: Input vs Output equality outside verification_field_ranges.

This validator ensures that input and example output spreadsheets are IDENTICAL
everywhere EXCEPT the cells explicitly listed in verification_field_ranges.

Goal:
Assert that the input and example output spreadsheets are IDENTICAL
everywhere EXCEPT the cells explicitly listed in verification_field_ranges.

Why:
Prompts may require edits in specific ranges; any unintended drift outside
those cells should fail verification.
"""

from __future__ import annotations
import re
from typing import Dict, List, Set, Tuple, Any, Union
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    pd = None

from urarovite.validators.base import BaseValidator, ValidationResult
from urarovite.core.exceptions import ValidationError
from urarovite.core.spreadsheet import SpreadsheetInterface

# Removed deprecated import - service is now passed as parameter
from urarovite.utils import (
    strip_outer_single_quotes,
    split_segments,
    extract_sheet_id,
)


class IdenticalOutsideRangesValidator(BaseValidator):
    """Validator that checks input vs output spreadsheets are identical
    outside specified ranges.
    """

    def __init__(self) -> None:
        super().__init__(
            validator_id="identical_outside_ranges",
            name="Identical Outside Ranges Validator",
            description="Ensures input and output spreadsheets are "
            "identical except in specified verification ranges",
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
        col_n = IdenticalOutsideRangesValidator._col_to_n(m.group(1))
        return int(m.group(2)) - 1, col_n - 1

    def _expand_a1_range(self, seg: str) -> Tuple[str, Tuple[int, int, int, int]]:
        """
        Accepts "'Tab'!A1:B9" or "A1:B9" (tab may be empty).
        Returns (tab, (r1,c1,r2,c2)) all zero-based inclusive.
        """
        s = seg.strip()
        m = self._A1_RNG.match(s if "!" in s else f"X!{s}")
        if not m:
            raise ValueError(f"Bad A1 range: {seg}")
        tab = (m.group("tab") or "").strip()
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

    def _excluded_cells_by_tab(
        self, ranges: List[str]
    ) -> Dict[str, Set[Tuple[int, int]]]:
        """Parse ranges and return excluded cells grouped by tab."""
        out: Dict[str, Set[Tuple[int, int]]] = {}
        for seg in ranges:
            seg = seg.strip()
            if not seg:
                continue
            tab, (r1, c1, r2, c2) = self._expand_a1_range(seg)
            if tab.startswith("'") and tab.endswith("'"):
                key = strip_outer_single_quotes(tab)
            else:
                key = tab
            s = out.setdefault(key, set())
            for rr in range(r1, r2 + 1):
                for cc in range(c1, c2 + 1):
                    s.add((rr, cc))
        return out

    @staticmethod
    def _a1_from_rc(r0: int, c0: int) -> str:
        """Convert 0-based row, col to A1 notation."""
        col_letter = IdenticalOutsideRangesValidator._n_to_col(c0 + 1)
        return f"{col_letter}{r0 + 1}"

    def _fetch_workbook_effective(
        self, service, spreadsheet_id: str
    ) -> Dict[str, List[List[Any]]]:
        """
        Pull effective values for all tabs with a tight fields mask.
        Returns: {tabTitle: [[cells...], ...]} with trimming of trailing
        empties.
        """
        resp = (
            service.spreadsheets()
            .get(
                spreadsheetId=spreadsheet_id,
                includeGridData=True,
                fields="sheets(properties.title,data.rowData.values.effectiveValue)",
            )
            .execute()
        )
        out: Dict[str, List[List[Any]]] = {}
        for sh in resp.get("sheets", []):
            title = sh["properties"]["title"]
            rows: List[List[Any]] = []
            for block in sh.get("data", []):
                for rd in block.get("rowData", []):
                    row = []
                    for cell in rd.get("values", []):
                        ev = cell.get("effectiveValue", {})
                        v = ev.get("stringValue")
                        if v is None:
                            v = ev.get("numberValue", ev.get("boolValue", ""))
                        row.append(v)
                    while row and row[-1] == "":
                        row.pop()
                    rows.append(row)
            while rows and not any(rows[-1]):
                rows.pop()
            out[title] = rows
        return out

    def _compare_outside(
        self,
        left: Dict[str, List[List[Any]]],
        right: Dict[str, List[List[Any]]],
        exclude: Dict[str, Set[Tuple[int, int]]],
    ) -> List[Dict[str, Any]]:
        """Compare two workbooks and return differences outside excluded
        ranges.
        """
        tabs = set(left.keys()) | set(right.keys())
        diffs: List[Dict[str, Any]] = []
        for tab in tabs:
            L = left.get(tab, [])
            R = right.get(tab, [])
            max_rows = max(len(L), len(R))
            max_cols = max(
                max((len(r) for r in L), default=0),
                max((len(r) for r in R), default=0),
            )
            skip = exclude.get(tab, set())
            for r in range(max_rows):
                for c in range(max_cols):
                    if (r, c) in skip:
                        continue
                    lv = L[r][c] if r < len(L) and c < len(L[r]) else ""
                    rv = R[r][c] if r < len(R) and c < len(R[r]) else ""
                    if lv != rv:
                        diffs.append(
                            {
                                "tab": tab,
                                "a1": self._a1_from_rc(r, c),
                                "row": r + 1,
                                "col": c + 1,
                                "input": lv,
                                "output": rv,
                            }
                        )
        return diffs

    def validate(
        self,
        spreadsheet_source: Union[str, Path, SpreadsheetInterface],
        mode: str,
        auth_credentials: Dict[str, Any] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Execute validation: input vs output must be identical OUTSIDE
        verification ranges.

        Args:
            spreadsheet_source: Either a Google Sheets URL, Excel file path,
                or SpreadsheetInterface
            mode: Either "fix" (not applicable) or "flag" (report only)
            auth_credentials: Authentication credentials (required for Google Sheets)
            **kwargs: Must contain 'row' with pandas Series or dict
                     containing the data

        Returns:
            Dict with validation results
        """

        def validation_logic(
            spreadsheet: SpreadsheetInterface, result: ValidationResult, **kwargs
        ) -> None:
            # Extract parameters
            row = kwargs.get("row")
            if row is None:
                # Return empty result if no row data provided
                result.set_automated_log("No flags found")
                return

            field = kwargs.get("field", "verification_field_ranges")
            input_col = kwargs.get("input_col", "input_sheet_url")
            output_col = kwargs.get("output_col", "example_output_sheet_url")
            max_report = kwargs.get("max_report", 100)

            # Parse ranges and extract sheet IDs
            ranges_str = row.get(field, "") or ""
            separator = kwargs.get("separator", None)  # Allow custom separator
            segments = split_segments(ranges_str, sep=separator)
            excluded = [s for s in segments if s]  # preserve original order

            input_sid = extract_sheet_id(row.get(input_col))
            output_sid = extract_sheet_id(row.get(output_col))
            if not input_sid or not output_sid:
                result.add_error("Missing input/output spreadsheet IDs")
                result.details["total_segments"] = len(segments)
                result.details["excluded"] = excluded
                result.details["diff_count"] = 0
                result.details["diffs"] = []
                result.set_automated_log("No flags found")
                return

            # Create sheets service for legacy API calls
            service = self._create_sheets_service(auth_credentials)

            try:
                # Fetch both workbooks
                left = self._fetch_workbook_effective(service, input_sid)
                right = self._fetch_workbook_effective(service, output_sid)

                # Compare outside excluded ranges
                exclude_map = self._excluded_cells_by_tab(excluded)
                diffs = self._compare_outside(left, right, exclude_map)

                for diff in diffs:
                    result.add_detailed_issue(
                        sheet_name=diff["tab"],
                        cell=diff["a1"],
                        message="Cell content differs outside of verification ranges",
                        value=f"Input: '{diff['input']}', Output: '{diff['output']}'",
                    )

                if result.flags_found > 0:
                    shown_diffs = diffs[:max_report]
                    result.details["diffs"] = shown_diffs
                    result.details["diff_count"] = len(diffs)
                    result.details["total_segments"] = len(segments)
                    result.details["excluded"] = excluded

                    if len(diffs) > max_report:
                        result.details["notes"] = (
                            f"Showing first {max_report} of {len(diffs)} diffs."
                        )

                    result.set_automated_log(
                        f"Found {result.flags_found} differences outside of specified ranges."
                    )
                else:
                    result.set_automated_log(
                        "No differences found outside of specified ranges."
                    )

            except Exception as e:
                error_msg = f"Failed to validate identical outside ranges: {str(e)}"
                result.add_error(error_msg)

        return self._execute_validation(
            validation_logic, spreadsheet_source, auth_credentials, **kwargs
        )


# Convenience function for backward compatibility
def run(
    row: Union[Dict[str, Any], "pd.Series"],
    field: str = "verification_field_ranges",
    input_col: str = "input_sheet_url",
    output_col: str = "example_output_sheet_url",
    max_report: int = 100,
) -> Dict[str, Any]:
    """
    Execute comparison: input vs output must be identical OUTSIDE
    verification ranges.
    This function provides backward compatibility with the original
    checker interface.
    """
    validator = IdenticalOutsideRangesValidator()
    return validator.validate(
        sheets_service=None,  # Not used by this validator
        sheet_id="",  # Not used by this validator
        mode="flag",
        row=row,
        field=field,
        input_col=input_col,
        output_col=output_col,
        max_report=max_report,
    )
