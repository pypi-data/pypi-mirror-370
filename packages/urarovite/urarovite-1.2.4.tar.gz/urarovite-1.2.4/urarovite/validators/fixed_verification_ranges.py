"""
Fixed Verification Field Ranges Tab Names Validator.

This validator checks "Fixed Verification Field Ranges" fields within Forte
spreadsheets to ensure proper tab name formatting in cell ranges.

Goal:
Ensure all tab names in cell ranges are properly enclosed in single apostrophes
and flag cases where tab names are missing entirely.

Why:
Proper tab name formatting ensures consistent parsing and reduces errors when
processing verification ranges. Tab names must be enclosed in single quotes
to handle spaces and special characters correctly.

Examples:
- Correct: 'FY2015_Present'!H2:H201, 'Grants'!A3:A143
- Fixable: Transactions!D2:D71 (missing quotes),
  Transactions'!D2:D71 (missing quote)
- Flag only: A1:K387 (missing tab name), 'F61' (no range)
"""

from __future__ import annotations
import re
from typing import Any, Dict, List, Union, Tuple
from pathlib import Path

from urarovite.validators.base import BaseValidator, ValidationResult

from urarovite.core.spreadsheet import SpreadsheetInterface


class FixedVerificationRangesValidator(BaseValidator):
    """Validator for proper tab name formatting in verification ranges."""

    def __init__(self) -> None:
        super().__init__(
            validator_id="fixed_verification_ranges",
            name="Fixed Verification Field Ranges",
            description=(
                "Ensures tab names in verification ranges are properly quoted "
                "with single apostrophes. Fixes missing quotes and flags "
                "ranges without tab names."
            ),
        )

    # Regular expression patterns for different range formats

    # Pattern for properly quoted tab names: 'TabName'!CellRange
    PROPERLY_QUOTED_PATTERN = re.compile(r"^'[^']+'![A-Z]+\d+(?::[A-Z]+\d+)?$")

    # Pattern for tab names missing quotes: TabName!CellRange (fixable)
    MISSING_QUOTES_PATTERN = re.compile(r"^([^'!]+)!([A-Z]+\d+(?::[A-Z]+\d+)?)$")

    # Pattern for tab names missing one quote (fixable)
    MISSING_ONE_QUOTE_PATTERN = re.compile(
        r"^(?:'([^'!]+)!|([^'!]+)'!)([A-Z]+\d+(?::[A-Z]+\d+)?)$"
    )

    # Pattern for ranges without tab names: A1:B10 or A1 (flag only)
    NO_TAB_NAME_PATTERN = re.compile(r"^[A-Z]+\d+(?::[A-Z]+\d+)?$")

    # Pattern for invalid formats like 'F61'
    INVALID_FORMAT_PATTERN = re.compile(r"^'[A-Z]+\d+'$")

    def _parse_range_entry(self, entry: str) -> Tuple[str, str, bool]:
        """
        Parse a single range entry and determine its format status.

        Args:
            entry: A single range entry (e.g., "'Grants'!A3:A143")

        Returns:
            Tuple of (issue_type, fixed_entry, can_fix)
            - issue_type: "valid", "missing_quotes", "missing_one_quote",
              "no_tab", "invalid"
            - fixed_entry: The corrected version if fixable
            - can_fix: Whether this issue can be automatically fixed
        """
        entry = entry.strip()

        if not entry:
            return "empty", "", False

        # Check if properly formatted
        if self.PROPERLY_QUOTED_PATTERN.match(entry):
            return "valid", entry, True

        # Check for missing quotes (fixable): TabName!A1:B2
        match = self.MISSING_QUOTES_PATTERN.match(entry)
        if match:
            tab_name, cell_range = match.groups()
            fixed_entry = f"'{tab_name}'!{cell_range}"
            return "missing_quotes", fixed_entry, True

        # Check for missing one quote (fixable): 'TabName!A1:B2 or
        # TabName'!A1:B2
        match = self.MISSING_ONE_QUOTE_PATTERN.match(entry)
        if match:
            # Groups: ('TabName' if starts with quote, 'TabName' if
            # ends with quote, 'cell_range')
            tab_with_start_quote, tab_with_end_quote, cell_range = match.groups()
            tab_name = tab_with_start_quote or tab_with_end_quote
            fixed_entry = f"'{tab_name}'!{cell_range}"
            return "missing_one_quote", fixed_entry, True

        # Check for ranges without tab names (flag only): A1:B2 or A1
        if self.NO_TAB_NAME_PATTERN.match(entry):
            return "no_tab", entry, False

        # Check for invalid formats like 'F61' (flag only)
        if self.INVALID_FORMAT_PATTERN.match(entry):
            return "invalid", entry, False

        # Unknown format (flag only)
        return "unknown", entry, False

    def _split_range_entries(self, ranges_str: str) -> List[str]:
        """
        Split a ranges string into individual entries.

        Args:
            ranges_str: Comma-separated range entries

        Returns:
            List of individual range entries
        """
        if not ranges_str or not isinstance(ranges_str, str):
            return []

        # Split by comma and clean up whitespace
        entries = [entry.strip() for entry in ranges_str.split(",")]
        return [entry for entry in entries if entry]

    def validate(
        self,
        spreadsheet_source: Union[str, Path, SpreadsheetInterface],
        mode: str,
        auth_credentials: Dict[str, Any] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Execute fixed verification ranges validation.

        Args:
            spreadsheet_source: Either a Google Sheets URL, Excel file path,
                or SpreadsheetInterface
            mode: Either "fix" (auto-correct quotes) or "flag" (report only)
            auth_credentials: Authentication credentials (required for Google Sheets)
            **kwargs: Additional parameters

        Returns:
            Dict with validation results
        """

        def validation_logic(
            spreadsheet: SpreadsheetInterface, result: ValidationResult, **kwargs
        ) -> None:
            """Format-agnostic validation logic."""

            flags_found = []
            fixes_by_sheet = {}

            def process_sheet(
                tab_name: str, data: List[List[Any]], result: ValidationResult
            ) -> None:
                """Process a single sheet for verification range issues."""
                sheet_fixes = []

                for row_idx, row in enumerate(data):
                    for col_idx, cell in enumerate(row):
                        if not cell or not isinstance(cell, str):
                            continue

                        # Look for cells that might contain verification
                        # ranges
                        cell_value = str(cell).strip()

                        # Skip cells that don't look like they contain ranges
                        if not any(char in cell_value for char in ["!", ":"]):
                            continue

                        # Check if this looks like a verification ranges field
                        # (contains range-like patterns)
                        entries = self._split_range_entries(cell_value)
                        if not entries:
                            continue

                        cell_ref = self._generate_cell_reference(
                            row_idx, col_idx, tab_name
                        )
                        fixed_entries = []
                        has_issues = False

                        for entry in entries:
                            issue_type, fixed_entry, can_fix = self._parse_range_entry(
                                entry
                            )

                            if issue_type == "valid":
                                fixed_entries.append(entry)
                            elif (
                                issue_type in ["missing_quotes", "missing_one_quote"]
                                and can_fix
                            ):
                                # Can be fixed
                                if mode == "fix":
                                    fixed_entries.append(fixed_entry)
                                    has_issues = True
                                    result.add_detailed_fix(
                                        sheet_name=tab_name,
                                        cell=cell_ref,
                                        message=(
                                            "Fixed missing apostrophes in tab "
                                            f"name: {entry} → {fixed_entry}"
                                        ),
                                        old_value=entry,
                                        new_value=fixed_entry,
                                    )
                                else:
                                    # Keep original for flagging
                                    fixed_entries.append(entry)
                                    flags_found.append(
                                        {
                                            "sheet": tab_name,
                                            "cell": cell_ref,
                                            "issue": (
                                                "Missing apostrophes in tab name"
                                            ),
                                            "value": entry,
                                            "suggested_fix": fixed_entry,
                                        }
                                    )
                                    result.add_detailed_issue(
                                        sheet_name=tab_name,
                                        cell=cell_ref,
                                        message=("Missing apostrophes in tab name"),
                                        value=entry,
                                    )
                            elif issue_type in ["no_tab", "invalid", "unknown"]:
                                # Can only be flagged
                                fixed_entries.append(entry)  # Keep original
                                issue_msg = {
                                    "no_tab": "Range missing tab name",
                                    "invalid": "Invalid range format",
                                    "unknown": "Unknown range format",
                                }.get(issue_type, "Range format issue")

                                flags_found.append(
                                    {
                                        "sheet": tab_name,
                                        "cell": cell_ref,
                                        "issue": issue_msg,
                                        "value": entry,
                                        "suggested_fix": None,
                                    }
                                )
                                result.add_detailed_issue(
                                    sheet_name=tab_name,
                                    cell=cell_ref,
                                    message=issue_msg,
                                    value=entry,
                                )
                            else:
                                # Keep as-is for other cases
                                fixed_entries.append(entry)

                        # If we made fixes, record them for sheet updating
                        if mode == "fix" and has_issues:
                            new_value = ", ".join(fixed_entries)
                            sheet_fixes.append(
                                {"row": row_idx, "col": col_idx, "new_value": new_value}
                            )

                # Store fixes for this sheet
                if sheet_fixes:
                    fixes_by_sheet[tab_name] = sheet_fixes

            # Process all sheets using the base class helper
            self._process_all_sheets(spreadsheet, process_sheet, result)

            # Apply fixes if in fix mode
            if mode == "fix" and fixes_by_sheet:
                for sheet_name, fixes in fixes_by_sheet.items():
                    # Get original data for this sheet
                    sheet_data = spreadsheet.get_sheet_data(sheet_name)
                    if sheet_data and sheet_data.values:
                        self._apply_fixes_to_sheet(
                            spreadsheet, sheet_name, sheet_data.values, fixes
                        )

                # Save changes (important for Excel files)
                spreadsheet.save()

            # Set automated log message
            if mode == "fix":
                if result.fixes_applied > 0:
                    result.set_automated_log(
                        f"Fixed {result.fixes_applied} tab name formatting issues"
                    )
                else:
                    result.set_automated_log(
                        "No tab name formatting issues found to fix"
                    )
            else:
                if result.flags_found > 0:
                    result.set_automated_log(
                        f"Found {result.flags_found} tab name formatting issues"
                    )
                else:
                    result.set_automated_log("No tab name formatting issues found")

        return self._execute_validation(
            validation_logic, spreadsheet_source, auth_credentials, **kwargs
        )


# Convenience function for direct usage
def run(ranges_str: str, mode: str = "flag") -> Dict[str, Any]:
    """
    Execute fixed verification ranges validation on a string directly.

    Args:
        ranges_str: String with ranges to validate
        mode: Validation mode ('flag' or 'fix')

    Returns:
        Dict with validation results
    """
    from .base import ValidationResult

    result = ValidationResult()
    validator = FixedVerificationRangesValidator()

    try:
        # Handle None or invalid input
        if ranges_str is None:
            result.add_error("ranges_str cannot be None")
            result.set_automated_log("Error during validation")
            return result.to_dict()
        entries = validator._split_range_entries(ranges_str)
        fixes_applied = 0
        flags_found = 0
        fixed_entries = []

        for entry in entries:
            issue_type, fixed_entry, can_fix = validator._parse_range_entry(entry)

            if issue_type == "valid":
                fixed_entries.append(entry)
            elif issue_type in ["missing_quotes", "missing_one_quote"] and can_fix:
                if mode == "fix":
                    fixed_entries.append(fixed_entry)
                    fixes_applied += 1
                else:
                    fixed_entries.append(entry)
                    flags_found += 1
            else:
                # Issues that can only be flagged
                fixed_entries.append(entry)
                flags_found += 1

        # Set results
        if mode == "fix":
            result.add_fix(fixes_applied)
            result.details["fixed_ranges"] = ", ".join(fixed_entries)
            # In fix mode, also report flags for issues that couldn't be
            # fixed
            unfixable_flags = (
                flags_found - fixes_applied if fixes_applied > 0 else flags_found
            )
            if unfixable_flags > 0:
                result.add_issue(unfixable_flags)
            if fixes_applied > 0:
                msg = f"Fixed {fixes_applied} tab name formatting issues"
            else:
                msg = "No tab name formatting issues found to fix"
            result.set_automated_log(msg)
        else:
            result.add_issue(flags_found)
            if flags_found > 0:
                msg = f"Found {flags_found} tab name formatting issues"
            else:
                msg = "No tab name formatting issues found"
            result.set_automated_log(msg)

        result.details["original"] = ranges_str or ""
        result.details["total_entries"] = len(entries)

    except Exception as e:
        result.add_error(f"Validation error: {str(e)}")
        result.set_automated_log("Error during validation")

    return result.to_dict()
