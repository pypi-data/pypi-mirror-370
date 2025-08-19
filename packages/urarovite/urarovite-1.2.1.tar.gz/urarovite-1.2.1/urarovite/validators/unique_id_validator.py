"""Unique ID Properties Validator for field masks.

This module implements validation for unique identifier fields in field masks,
including duplicate detection, format consistency, and missing ID validation.
"""

import re
from typing import Any, Dict, List, Set, Union, Optional
from pathlib import Path

from urarovite.validators.base import BaseValidator, ValidationResult
from urarovite.core.exceptions import ValidationError
from urarovite.core.spreadsheet import SpreadsheetInterface

# Common ID field patterns and their validation rules
ID_FIELD_PATTERNS = {
    # Common ID field names (case-insensitive)
    "id_fields": [
        r"^id$",
        r"^_?id$",
        r"^.*_id$",
        r"^id_.*$",  # Basic ID patterns
        r"^uuid$",
        r"^guid$",
        r"^key$",
        r"^pk$",  # Alternative ID names
        r"^reference$",
        r"^ref$",
        r"^code$",  # Reference patterns
        r"^.*_key$",
        r"^key_.*$",  # Key patterns
    ],
    # Common ID format patterns
    "id_formats": {
        "uuid": r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
        "numeric": r"^\d+$",
        "alphanumeric": r"^[a-zA-Z0-9]+$",
        "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        "url": r"^https?://[^\s/$.?#].[^\s]*$",
    },
}


class UniqueIDValidator(BaseValidator):
    """Validator for checking unique identifier properties in field masks."""

    def __init__(self) -> None:
        super().__init__(
            validator_id="unique_id_properties",
            name="Validate Unique ID Properties",
            description="Validates unique identifier fields in field masks, detects duplicates, ensures format consistency, and flags missing/malformed IDs.",
        )

    def validate(
        self,
        spreadsheet_source: Union[str, Path, SpreadsheetInterface],
        mode: str,
        auth_credentials: Dict[str, Any] = None,
        id_column_patterns: Optional[List[str]] = None,
        strict_format_checking: bool = True,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Validate unique identifier properties in field masks.

        Args:
            spreadsheet_source: Either a Google Sheets URL, Excel file path,
                or SpreadsheetInterface
            mode: Either "fix" (auto-correct where possible) or "flag" (report only)
            auth_credentials: Authentication credentials (required for Google Sheets)
            id_column_patterns: Custom patterns for identifying ID columns
            strict_format_checking: Whether to strictly validate ID formats

        Returns:
            Dict with validation results
        """

        def validation_logic(
            spreadsheet: SpreadsheetInterface, result: ValidationResult, **kwargs
        ) -> None:
            # Get all sheet data
            data, sheet_name = self._get_all_sheet_data(spreadsheet)

            if not data:
                result.add_error("No data found to validate")
                result.set_automated_log("No data found to validate")
                return

            # Identify ID columns from headers
            headers = data[0] if data else []
            id_columns = self._identify_id_columns(headers, id_column_patterns)

            if not id_columns:
                result.set_automated_log("No ID columns identified in field mask")
                return

            # Validate each ID column
            validation_results = {
                "id_columns": id_columns,
                "duplicates": [],
                "format_flags": [],
                "missing_ids": [],
                "suggestions": [],
            }

            for col_idx, col_name in id_columns:
                col_results = self._validate_id_column(
                    data, col_idx, col_name, strict_format_checking
                )

                # Merge results
                validation_results["duplicates"].extend(col_results["duplicates"])
                validation_results["format_flags"].extend(col_results["format_flags"])
                validation_results["missing_ids"].extend(col_results["missing_ids"])
                validation_results["suggestions"].extend(col_results["suggestions"])

            # Apply fixes if in fix mode
            if mode == "fix" and (
                validation_results["duplicates"] or validation_results["format_flags"]
            ):
                fixed_data = self._apply_id_fixes(data, validation_results)
                self._update_sheet_data(spreadsheet, sheet_name, fixed_data)
                spreadsheet.save()

                # Report detailed fixes for duplicates
                for duplicate in validation_results["duplicates"]:
                    for i, row_num in enumerate(
                        duplicate["rows"][1:], 1
                    ):  # Skip first occurrence
                        cell_ref = self._generate_cell_reference(
                            row_num - 2, duplicate.get("col_idx", 0), sheet_name
                        )
                        suffix = f"_{i:03d}"
                        new_value = f"{duplicate['value']}{suffix}"
                        result.add_detailed_fix(
                            sheet_name=sheet_name,
                            cell=cell_ref,
                            message=f"Fixed duplicate ID '{duplicate['value']}' by adding unique suffix",
                            old_value=duplicate["value"],
                            new_value=new_value,
                        )

                # Report detailed fixes for format flags
                for format_issue in validation_results["format_flags"]:
                    cell_ref = self._generate_cell_reference(
                        format_issue["row"] - 2, format_issue["col"] - 1, sheet_name
                    )
                    # Apply the same fixing logic to show what the new value would be
                    fixed_value = self._fix_id_format(format_issue["value"])
                    result.add_detailed_fix(
                        sheet_name=sheet_name,
                        cell=cell_ref,
                        message=f"Fixed format issue: {format_issue['details']}",
                        old_value=format_issue["value"],
                        new_value=fixed_value,
                    )

                total_fixes = len(validation_results["duplicates"]) + len(
                    validation_results["format_flags"]
                )
                result.set_automated_log(
                    f"Applied {total_fixes} ID fixes: {len(validation_results['duplicates'])} duplicates and {len(validation_results['format_flags'])} format flags"
                )
            else:
                # Flag mode - add detailed issue reporting
                # Report duplicates
                for duplicate in validation_results["duplicates"]:
                    for row_num in duplicate["rows"]:
                        cell_ref = self._generate_cell_reference(
                            row_num - 2, duplicate.get("col_idx", 0), sheet_name
                        )
                        result.add_detailed_issue(
                            sheet_name=sheet_name,
                            cell=cell_ref,
                            message=f"Duplicate ID '{duplicate['value']}' found in column '{duplicate['column_name']}'",
                            value=duplicate["value"],
                        )

                # Report format flags
                for format_issue in validation_results["format_flags"]:
                    cell_ref = self._generate_cell_reference(
                        format_issue["row"] - 2, format_issue["col"] - 1, sheet_name
                    )
                    result.add_detailed_issue(
                        sheet_name=sheet_name,
                        cell=cell_ref,
                        message=f"Format issue in ID column '{format_issue['column_name']}': {format_issue['details']}",
                        value=format_issue["value"],
                    )

                # Report missing IDs
                for missing in validation_results["missing_ids"]:
                    cell_ref = self._generate_cell_reference(
                        missing["row"] - 2, missing["col"] - 1, sheet_name
                    )
                    result.add_detailed_issue(
                        sheet_name=sheet_name,
                        cell=cell_ref,
                        message=f"Missing ID in column '{missing['column_name']}'",
                        value="",
                    )

                total_flags = (
                    len(validation_results["duplicates"])
                    + len(validation_results["format_flags"])
                    + len(validation_results["missing_ids"])
                )

                if total_flags > 0:
                    result.set_automated_log(
                        f"Found {total_flags} ID validation flags: "
                        f"{len(validation_results['duplicates'])} duplicates, "
                        f"{len(validation_results['format_flags'])} format flags, "
                        f"{len(validation_results['missing_ids'])} missing IDs"
                    )
                else:
                    result.set_automated_log("No ID validation flags found")

            # Set result details for additional context
            result.details["id_columns"] = validation_results["id_columns"]
            result.details["suggestions"] = validation_results["suggestions"]

        return self._execute_validation(
            validation_logic, spreadsheet_source, auth_credentials, **kwargs
        )

    def _identify_id_columns(
        self, headers: List[str], custom_patterns: Optional[List[str]] = None
    ) -> List[tuple[int, str]]:
        """Identify columns that contain ID fields based on header names.

        Args:
            headers: List of column headers
            custom_patterns: Additional patterns for ID column identification

        Returns:
            List of tuples (column_index, column_name) for identified ID columns
        """
        id_columns = []
        patterns = ID_FIELD_PATTERNS["id_fields"].copy()

        if custom_patterns:
            patterns.extend(custom_patterns)

        for col_idx, header in enumerate(headers):
            header_str = str(header).lower().strip()

            # Check if header matches any ID pattern
            for pattern in patterns:
                if re.match(pattern, header_str, re.IGNORECASE):
                    id_columns.append((col_idx, str(header)))
                    break

        return id_columns

    def _validate_id_column(
        self,
        data: List[List[Any]],
        col_idx: int,
        col_name: str,
        strict_format_checking: bool,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Validate a single ID column for various flags.

        Args:
            data: 2D list of spreadsheet data
            col_idx: Column index (0-based)
            col_name: Column name
            strict_format_checking: Whether to strictly validate formats

        Returns:
            Dictionary containing validation results
        """
        results = {
            "duplicates": [],
            "format_flags": [],
            "missing_ids": [],
            "suggestions": [],
        }

        # Skip header row
        data_rows = data[1:] if len(data) > 1 else []

        # Track seen values and their row numbers
        seen_values: Dict[str, List[int]] = {}
        empty_rows = []

        for row_idx, row in enumerate(data_rows):
            if col_idx >= len(row):
                continue

            cell_value = row[col_idx]
            row_number = row_idx + 2  # +2 because we skip header and 0-based indexing

            # Check for missing/empty IDs
            if cell_value is None or cell_value == "" or str(cell_value).strip() == "":
                empty_rows.append(
                    {
                        "row": row_number,
                        "col": col_idx + 1,
                        "column_name": col_name,
                        "issue": "missing_id",
                    }
                )
                continue

            # Convert to string for processing
            str_value = str(cell_value).strip()

            # Check for duplicates
            if str_value in seen_values:
                seen_values[str_value].append(row_number)
                # Only add to duplicates list once per value
                if len(seen_values[str_value]) == 2:
                    results["duplicates"].append(
                        {
                            "value": str_value,
                            "rows": seen_values[str_value],
                            "column_name": col_name,
                            "col_idx": col_idx,
                            "issue": "duplicate_id",
                        }
                    )
            else:
                seen_values[str_value] = [row_number]

            # Check format consistency if strict checking is enabled
            if strict_format_checking:
                format_issue = self._check_id_format(str_value, col_name)
                if format_issue:
                    results["format_flags"].append(
                        {
                            "row": row_number,
                            "col": col_idx + 1,
                            "value": str_value,
                            "column_name": col_name,
                            "issue": "format_inconsistency",
                            "details": format_issue,
                        }
                    )

        # Add missing ID results
        results["missing_ids"] = empty_rows

        # Generate suggestions for improvement
        if results["duplicates"] or results["format_flags"]:
            results["suggestions"].append(
                {
                    "type": "general",
                    "message": f"Consider implementing data validation rules for column '{col_name}'",
                }
            )

        return results

    def _check_id_format(self, value: str, column_name: str) -> Optional[str]:
        """Check if an ID value matches expected format patterns.

        Args:
            value: The ID value to check
            column_name: Name of the column for context

        Returns:
            Error message if format is invalid, None if valid
        """
        # Check for common flags first (before format patterns)
        if len(value) < 3:
            return "ID value too short (minimum 3 characters recommended)"

        if len(value) > 100:
            return "ID value too long (maximum 100 characters recommended)"

        # Check for suspicious patterns
        if re.search(r"\s+", value):
            return "ID contains whitespace (not recommended)"

        # Check against common ID formats first (to allow valid formats with special chars)
        for format_name, pattern in ID_FIELD_PATTERNS["id_formats"].items():
            if re.match(pattern, value, re.IGNORECASE):
                return None  # Valid format

        # Check for problematic special characters (only if not a valid format)
        if re.search(r"[^\w\-_\.@]", value):
            return "ID contains special characters that may cause flags"

        return None  # Acceptable format

    def _fix_id_format(self, value: str) -> str:
        """Apply basic formatting fixes to an ID value.

        Args:
            value: The original ID value

        Returns:
            The fixed ID value
        """
        # Apply basic formatting fixes
        fixed_value = str(value).strip()

        # Remove extra whitespace
        fixed_value = re.sub(r"\s+", " ", fixed_value)

        # Remove problematic characters
        fixed_value = re.sub(r"[^\w\-_\.@]", "_", fixed_value)

        # Ensure minimum length
        if len(fixed_value) < 3:
            fixed_value = f"ID_{fixed_value}"

        return fixed_value

    def _apply_id_fixes(
        self, data: List[List[Any]], validation_results: Dict[str, List[Dict[str, Any]]]
    ) -> List[List[Any]]:
        """Apply fixes to ID validation flags where possible.

        Args:
            data: Original spreadsheet data
            validation_results: Results from validation

        Returns:
            Fixed data (copy of original with fixes applied)
        """
        # Create a copy of the data to avoid modifying the original
        fixed_data = [row[:] for row in data]

        # Fix duplicates by appending unique suffixes
        for duplicate in validation_results["duplicates"]:
            value = duplicate["value"]
            rows = duplicate["rows"]

            # Keep the first occurrence, modify the rest
            for i, row_num in enumerate(rows[1:], 1):
                # Convert to 0-based index and account for header
                data_row_idx = row_num - 2
                col_idx = None

                # Find the column index
                col_idx = None
                for col_idx, col_name in validation_results["id_columns"]:
                    if col_name == duplicate["column_name"]:
                        break

                if col_idx is not None and data_row_idx < len(fixed_data):
                    # Create unique suffix
                    suffix = f"_{i:03d}"
                    new_value = f"{value}{suffix}"

                    # Ensure the row has enough columns
                    while len(fixed_data[data_row_idx]) <= col_idx:
                        fixed_data[data_row_idx].append("")

                    fixed_data[data_row_idx][col_idx] = new_value

        # Fix format flags where possible
        for format_issue in validation_results["format_flags"]:
            row_idx = (
                format_issue["row"] - 2
            )  # Convert to 0-based and account for header
            col_idx = format_issue["col"] - 1  # Convert to 1-based

            if row_idx < len(fixed_data) and col_idx < len(fixed_data[row_idx]):
                original_value = str(fixed_data[row_idx][col_idx])

                # Apply basic formatting fixes
                fixed_value = original_value.strip()

                # Remove extra whitespace
                fixed_value = re.sub(r"\s+", " ", fixed_value)

                # Remove problematic characters
                fixed_value = re.sub(r"[^\w\-_\.@]", "_", fixed_value)

                # Ensure minimum length
                if len(fixed_value) < 3:
                    fixed_value = f"ID_{fixed_value}"

                fixed_data[row_idx][col_idx] = fixed_value

        return fixed_data
