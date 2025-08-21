"""Duplicate and overlapping ranges validator for Google Sheets and Excel files.

This validator detects overlapping verification ranges, duplicate range
definitions, conflicting range specifications, and suggests range optimization.
"""

import re
from typing import Any, Dict, List, Tuple, Union
from pathlib import Path

from urarovite.validators.base import BaseValidator, ValidationResult
from urarovite.core.spreadsheet import SpreadsheetInterface


class DuplicateOverlappingRangesValidator(BaseValidator):
    """Validator for detecting duplicate and overlapping A1 ranges."""

    def __init__(self) -> None:
        super().__init__(
            validator_id="duplicate_overlapping_ranges",
            name="Duplicate and Overlapping Ranges Validator",
            description=(
                "Detects overlapping verification ranges, duplicate range "
                "definitions, conflicting range specifications, and suggests "
                "range optimization"
            ),
        )

    # A1 range parsing regex patterns
    _A1_RANGE_PATTERN = re.compile(
        r"^(?:'?(?P<sheet>[^'!]+)'?!)?(?P<start>[A-Z]+[0-9]+)"
        r"(?::(?P<end>[A-Z]+[0-9]+))?$"
    )
    _A1_CELL_PATTERN = re.compile(r"^([A-Z]+)([0-9]+)$")

    def validate(
        self,
        spreadsheet_source: Union[str, Path, SpreadsheetInterface],
        mode: str,
        auth_credentials: Dict[str, Any] = None,
        range_columns: List[int] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Validate ranges for duplicates and overlaps.

        Args:
            spreadsheet_source: Either a Google Sheets URL, Excel file path,
                or SpreadsheetInterface
            mode: Either "fix" (suggest optimizations) or "flag" (report only)
            auth_credentials: Authentication credentials (required for
                Google Sheets)
            range_columns: List of 1-based column indices containing A1 ranges

        Returns:
            Dict with validation results
        """

        def validation_logic(
            spreadsheet: SpreadsheetInterface, result: ValidationResult, **kwargs
        ) -> None:
            """Format-agnostic validation logic."""
            # Get parameters
            mode = kwargs.get("mode", "flag")
            range_columns = kwargs.get("range_columns")

            # Get all sheet data
            data, sheet_name = self._get_all_sheet_data(spreadsheet)

            if not data:
                result.add_error("Sheet is empty - no data to validate")
                result.details["valid_ranges"] = 0
                result.details["duplicate_ranges"] = []
                result.details["overlapping_ranges"] = []
                result.details["conflicting_ranges"] = []
                result.details["optimization_suggestions"] = []
                result.set_automated_log("Sheet is empty - no data to validate")
                return

            # Auto-detect range columns if not specified
            detected_range_columns = range_columns
            if detected_range_columns is None:
                detected_range_columns = self._detect_range_columns(data)

            if not detected_range_columns:
                result.details["message"] = "No range columns found in data"
                result.details["valid_ranges"] = 0
                result.details["duplicate_ranges"] = []
                result.details["overlapping_ranges"] = []
                result.details["conflicting_ranges"] = []
                result.details["optimization_suggestions"] = []
                result.set_automated_log("No range columns detected")
                return

            # Collect all ranges from the specified columns
            all_ranges = []
            for row_idx, row in enumerate(data):
                if row_idx == 0:  # Skip header row
                    continue

                for col_idx in detected_range_columns:
                    if col_idx <= len(row):
                        cell_value = row[col_idx - 1]  # Convert to 0-based
                        if cell_value and isinstance(cell_value, str):
                            ranges = self._parse_ranges_string(cell_value)
                            for range_info in ranges:
                                if range_info:
                                    range_info["source"] = {
                                        "row": row_idx
                                        + 1,  # 1-based for user reference
                                        "col": col_idx,
                                        "cell": self._generate_cell_reference(
                                            row_idx, col_idx, sheet_name
                                        ),
                                    }
                                    all_ranges.append(range_info)

            if not all_ranges:
                result.details["message"] = "No valid ranges found in specified columns"
                result.details["valid_ranges"] = 0
                result.details["duplicate_ranges"] = []
                result.details["overlapping_ranges"] = []
                result.details["conflicting_ranges"] = []
                result.details["optimization_suggestions"] = []
                result.set_automated_log("No valid ranges found")
                return

            # Analyze ranges for flags
            duplicate_ranges = self._find_duplicate_ranges(all_ranges)
            overlapping_ranges = self._find_overlapping_ranges(all_ranges)
            conflicting_ranges = self._find_conflicting_ranges(all_ranges)
            optimization_suggestions = self._generate_optimization_suggestions(
                all_ranges
            )

            # Handle mode-specific reporting
            total_flags = (
                len(duplicate_ranges)
                + len(overlapping_ranges)
                + len(conflicting_ranges)
            )

            if mode == "fix":
                # This validator is flag-only, so no fixes are applied
                # But we still report what would be optimized
                result.set_automated_log(
                    f"Detected {total_flags} flags that require manual resolution: "
                    f"{len(duplicate_ranges)} duplicates, {len(overlapping_ranges)} overlaps, "
                    f"{len(conflicting_ranges)} conflicts. See optimization suggestions."
                )
            else:
                # Flag mode - add detailed issue reporting
                self._report_detailed_flags(
                    result,
                    sheet_name,
                    duplicate_ranges,
                    overlapping_ranges,
                    conflicting_ranges,
                )

                if total_flags > 0:
                    result.set_automated_log(
                        f"Found {total_flags} flags: {len(duplicate_ranges)} duplicates, "
                        f"{len(overlapping_ranges)} overlaps, {len(conflicting_ranges)} conflicts"
                    )
                else:
                    result.set_automated_log("No duplicate or overlapping ranges found")

            # Set details for both modes
            result.details["valid_ranges"] = len(all_ranges)
            result.details["duplicate_ranges"] = duplicate_ranges
            result.details["overlapping_ranges"] = overlapping_ranges
            result.details["conflicting_ranges"] = conflicting_ranges
            result.details["optimization_suggestions"] = optimization_suggestions

        return self._execute_validation(
            validation_logic,
            spreadsheet_source,
            auth_credentials,
            mode=mode,
            range_columns=range_columns,
            **kwargs,
        )

    def _report_detailed_flags(
        self,
        result: ValidationResult,
        sheet_name: str,
        duplicate_ranges: List[Dict[str, Any]],
        overlapping_ranges: List[Dict[str, Any]],
        conflicting_ranges: List[Dict[str, Any]],
    ) -> None:
        """Report detailed flags using BaseValidator's add_detailed_issue method.

        Args:
            result: ValidationResult instance
            sheet_name: Name of the sheet being validated
            duplicate_ranges: List of duplicate range flags
            overlapping_ranges: List of overlapping range flags
            conflicting_ranges: List of conflicting range flags
        """
        # Report duplicate range flags
        for duplicate in duplicate_ranges:
            duplicate_info = duplicate["duplicate"]
            original_info = duplicate["original"]

            result.add_detailed_issue(
                sheet_name=sheet_name,
                cell=duplicate_info["source"]["cell"],
                message=f"Duplicate range '{duplicate_info['range_string']}' "
                f"already defined at {original_info['source']['cell']}",
                value=duplicate_info["range_string"],
            )

        # Report overlapping range flags
        for overlap in overlapping_ranges:
            range1 = overlap["range1"]
            range2 = overlap["range2"]
            overlap_area = overlap["overlap_area"]

            result.add_detailed_issue(
                sheet_name=sheet_name,
                cell=range1["source"]["cell"],
                message=f"Range '{range1['range_string']}' overlaps with "
                f"'{range2['range_string']}' at {range2['source']['cell']} "
                f"(overlap area: {overlap_area} cells)",
                value=range1["range_string"],
            )

        # Report conflicting range flags
        for conflict in conflicting_ranges:
            range1 = conflict["range1"]
            range2 = conflict["range2"]
            conflict_type = conflict["conflict_type"]

            result.add_detailed_issue(
                sheet_name=sheet_name,
                cell=range1["source"]["cell"],
                message=f"Range '{range1['range_string']}' conflicts with "
                f"'{range2['range_string']}' at {range2['source']['cell']}: {conflict_type}",
                value=range1["range_string"],
            )

    def _detect_range_columns(self, data: List[List[Any]]) -> List[int]:
        """Auto-detect columns containing A1 ranges."""
        if not data or len(data) < 2:  # Need at least header + 1 data row
            return []

        range_columns = []
        headers = data[0]

        for col_idx, header in enumerate(headers, 1):  # 1-based column index
            if not header:
                continue

            header_str = str(header).lower()
            # Look for columns that might contain ranges
            if any(
                keyword in header_str
                for keyword in [
                    "range",
                    "verification",
                    "field",
                    "check",
                    "validate",
                    "compare",
                ]
            ):
                range_columns.append(col_idx)
                continue

            # Check if the column actually contains range data
            range_count = 0
            total_cells = 0

            for row_idx in range(1, min(len(data), 10)):  # Check first 10 data rows
                if col_idx <= len(data[row_idx]):
                    cell_value = data[row_idx][col_idx - 1]
                    if cell_value and isinstance(cell_value, str):
                        total_cells += 1
                        if self._contains_a1_ranges(cell_value):
                            range_count += 1

            # If more than 50% of cells contain ranges, consider it a range column
            if total_cells > 0 and (range_count / total_cells) > 0.5:
                range_columns.append(col_idx)

        return range_columns

    def _contains_a1_ranges(self, value: str) -> bool:
        """Check if a string contains A1 range patterns."""
        if not value or not isinstance(value, str):
            return False

        # Look for A1 range patterns
        a1_patterns = [
            r"[A-Z]+\d+:[A-Z]+\d+",  # A1:B2
            r"[A-Z]+\d+",  # A1
            r"'[^']+'![A-Z]+\d+",  # 'Sheet'!A1
            r"'[^']+'![A-Z]+\d+:[A-Z]+\d+",  # 'Sheet'!A1:B2
        ]

        for pattern in a1_patterns:
            if re.search(pattern, value):
                return True

        return False

    def _parse_ranges_string(self, ranges_str: str) -> List[Dict[str, Any]]:
        """Parse a string containing multiple A1 ranges separated by @@."""
        if not ranges_str or not isinstance(ranges_str, str):
            return []

        ranges = []
        # Split by @@ separator (common in verification field ranges)
        range_segments = ranges_str.split("@@")

        for segment in range_segments:
            segment = segment.strip()
            if not segment:
                continue

            range_info = self._parse_single_range(segment)
            if range_info:
                ranges.append(range_info)

        return ranges

    def _parse_single_range(self, range_str: str) -> Dict[str, Any]:
        """Parse a single A1 range string."""
        if not range_str or not isinstance(range_str, str):
            return {}

        range_str = range_str.strip()

        # Match the A1 range pattern
        match = self._A1_RANGE_PATTERN.match(range_str)
        if not match:
            return {}

        sheet_name = match.group("sheet") or ""
        start_cell = match.group("start")
        end_cell = match.group("end") or start_cell

        # Parse start and end coordinates
        start_coords = self._parse_cell_coordinates(start_cell)
        end_coords = self._parse_cell_coordinates(end_cell)

        if not start_coords or not end_coords:
            return {}

        return {
            "sheet": sheet_name.strip("'"),
            "start_cell": start_cell,
            "end_cell": end_cell,
            "start_row": start_coords[0],
            "start_col": start_coords[1],
            "end_row": end_coords[0],
            "end_col": end_coords[1],
            "range_string": range_str,
        }

    def _parse_cell_coordinates(self, cell: str) -> Tuple[int, int]:
        """Parse A1 cell notation to (row, col) coordinates."""
        match = self._A1_CELL_PATTERN.match(cell)
        if not match:
            return None, None

        col_str = match.group(1)
        row_str = match.group(2)

        # Convert column letters to number (A=1, B=2, AA=27, etc.)
        col_num = 0
        for char in col_str:
            col_num = col_num * 26 + (ord(char.upper()) - ord("A") + 1)

        # Convert row string to number
        try:
            row_num = int(row_str)
        except ValueError:
            return None, None

        return row_num, col_num

    def _find_duplicate_ranges(
        self, ranges: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Find ranges that are exactly the same."""
        duplicates = []
        seen_ranges = set()

        for range_info in ranges:
            # Create a key for comparison (ignoring source location)
            range_key = (
                range_info["sheet"],
                range_info["start_row"],
                range_info["start_col"],
                range_info["end_row"],
                range_info["end_col"],
            )

            if range_key in seen_ranges:
                # Find the original range to report both locations
                original_range = next(
                    r
                    for r in ranges
                    if (
                        r["sheet"] == range_key[0]
                        and r["start_row"] == range_key[1]
                        and r["start_col"] == range_key[2]
                        and r["end_row"] == range_key[3]
                        and r["end_col"] == range_key[4]
                        and r["source"]["cell"] != range_info["source"]["cell"]
                    )
                )

                duplicates.append(
                    {
                        "duplicate": range_info,
                        "original": original_range,
                        "issue": "Duplicate range definition",
                    }
                )
            else:
                seen_ranges.add(range_key)

        return duplicates

    def _find_overlapping_ranges(
        self, ranges: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Find ranges that overlap with each other."""
        overlaps = []

        for i, range1 in enumerate(ranges):
            for j, range2 in enumerate(ranges[i + 1 :], i + 1):
                if self._ranges_overlap(range1, range2):
                    overlaps.append(
                        {
                            "range1": range1,
                            "range2": range2,
                            "overlap_area": self._calculate_overlap_area(
                                range1, range2
                            ),
                            "issue": "Overlapping ranges",
                        }
                    )

        return overlaps

    def _ranges_overlap(self, range1: Dict[str, Any], range2: Dict[str, Any]) -> bool:
        """Check if two ranges overlap."""
        # Ranges must be on the same sheet to overlap
        if range1["sheet"] != range2["sheet"]:
            return False

        # Check for overlap using rectangle intersection logic
        # Range1: (start_row1, start_col1) to (end_row1, end_col1)
        # Range2: (start_row2, start_col2) to (end_row2, end_col2)

        # No overlap if one range is completely to the left, right, above, or below
        if (
            range1["end_col"] < range2["start_col"]
            or range2["end_col"] < range1["start_col"]
            or range1["end_row"] < range2["start_row"]
            or range2["end_row"] < range1["start_row"]
        ):
            return False

        return True

    def _calculate_overlap_area(
        self, range1: Dict[str, Any], range2: Dict[str, Any]
    ) -> int:
        """Calculate the area of overlap between two ranges."""
        if not self._ranges_overlap(range1, range2):
            return 0

        # Calculate overlap dimensions
        overlap_start_row = max(range1["start_row"], range2["start_row"])
        overlap_end_row = min(range1["end_row"], range2["end_row"])
        overlap_start_col = max(range1["start_col"], range2["start_col"])
        overlap_end_col = min(range1["end_col"], range2["end_col"])

        overlap_height = overlap_end_row - overlap_start_row + 1
        overlap_width = overlap_end_col - overlap_start_col + 1

        return overlap_height * overlap_width

    def _find_conflicting_ranges(
        self, ranges: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Find ranges that have conflicting specifications."""
        conflicts = []

        for i, range1 in enumerate(ranges):
            for j, range2 in enumerate(ranges[i + 1 :], i + 1):
                conflict = self._detect_range_conflict(range1, range2)
                if conflict:
                    conflicts.append(
                        {
                            "range1": range1,
                            "range2": range2,
                            "conflict_type": conflict,
                            "issue": f"Conflicting range specification: {conflict}",
                        }
                    )

        return conflicts

    def _detect_range_conflict(
        self, range1: Dict[str, Any], range2: Dict[str, Any]
    ) -> str:
        """Detect conflicts between two ranges."""
        # Check for same sheet, same area, but different specifications
        if (
            range1["sheet"] == range2["sheet"]
            and range1["start_row"] == range2["start_row"]
            and range1["start_col"] == range2["start_col"]
            and range1["end_row"] == range2["end_row"]
            and range1["end_col"] == range2["end_col"]
        ):
            # Same area but different string representations
            if range1["range_string"] != range2["range_string"]:
                return "Same area with different notation"

        # Check for ranges that should be identical but aren't
        if (
            range1["sheet"] == range2["sheet"]
            and abs(range1["start_row"] - range2["start_row"]) <= 1
            and abs(range1["start_col"] - range2["start_col"]) <= 1
            and abs(range1["end_row"] - range2["end_row"]) <= 1
            and abs(range1["end_col"] - range2["end_col"]) <= 1
        ):
            return "Nearly identical ranges with slight differences"

        return None

    def _generate_optimization_suggestions(
        self, ranges: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate suggestions for range optimization."""
        suggestions = []

        # Group ranges by sheet
        ranges_by_sheet = {}
        for range_info in ranges:
            sheet = range_info["sheet"]
            if sheet not in ranges_by_sheet:
                ranges_by_sheet[sheet] = []
            ranges_by_sheet[sheet].append(range_info)

        # Analyze each sheet for optimization opportunities
        for sheet, sheet_ranges in ranges_by_sheet.items():
            if len(sheet_ranges) < 2:
                continue

            # Sort ranges by position
            sheet_ranges.sort(key=lambda r: (r["start_row"], r["start_col"]))

            # Look for adjacent ranges that could be merged
            for i in range(len(sheet_ranges) - 1):
                range1 = sheet_ranges[i]
                range2 = sheet_ranges[i + 1]

                # Check if ranges are adjacent horizontally
                if (
                    range1["start_row"] == range2["start_row"]
                    and range1["end_row"] == range2["end_row"]
                    and range1["end_col"] + 1 == range2["start_col"]
                ):
                    suggestions.append(
                        {
                            "type": "merge_horizontal",
                            "ranges": [range1, range2],
                            "suggestion": f"Merge adjacent horizontal ranges: {range1['range_string']} and {range2['range_string']}",
                            "optimized_range": f"'{sheet}'!{self._get_cell_ref(range1['start_row'], range1['start_col'])}:{self._get_cell_ref(range2['end_row'], range2['end_col'])}",
                        }
                    )

                # Check if ranges are adjacent vertically
                elif (
                    range1["start_col"] == range2["start_col"]
                    and range1["end_col"] == range2["end_col"]
                    and range1["end_row"] + 1 == range2["start_row"]
                ):
                    suggestions.append(
                        {
                            "type": "merge_vertical",
                            "ranges": [range1, range2],
                            "suggestion": f"Merge adjacent vertical ranges: {range1['range_string']} and {range2['range_string']}",
                            "optimized_range": f"'{sheet}'!{self._get_cell_ref(range1['start_row'], range1['start_col'])}:{self._get_cell_ref(range2['end_row'], range2['end_col'])}",
                        }
                    )

            # Look for ranges that could be simplified
            for range_info in sheet_ranges:
                if (
                    range_info["start_row"] == range_info["end_row"]
                    and range_info["start_col"] == range_info["end_col"]
                ):
                    suggestions.append(
                        {
                            "type": "simplify_single_cell",
                            "ranges": [range_info],
                            "suggestion": f"Single cell range can be simplified: {range_info['range_string']}",
                            "optimized_range": f"'{sheet}'!{self._get_cell_ref(range_info['start_row'], range_info['start_col'])}",
                        }
                    )

        return suggestions

    def _get_cell_ref(self, row: int, col: int) -> str:
        """Convert row and column numbers to A1 notation."""
        col_letter = ""
        col_num = col
        while col_num > 0:
            col_num -= 1
            col_letter = chr(col_num % 26 + ord("A")) + col_letter
            col_num //= 26

        return f"{col_letter}{row}"
