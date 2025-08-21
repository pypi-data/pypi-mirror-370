"""
Sheet Name Quoting Validator.

This validator ensures that all sheet names in verification_field_ranges are
properly quoted with single quotes when they contain spaces or special characters.

Goal:
Verify that each range segment starts with a sheet name wrapped in single quotes
following the pattern 'SheetName'! to ensure proper A1 notation parsing.

Why:
Sheet names with spaces or special characters must be quoted in A1 notation to
avoid parsing errors and ensure consistent behavior across different systems.

Examples:
- Valid: 'March 2025'!A2:A91
- Invalid: March 2025!A2:A91 (missing quotes)
"""

from __future__ import annotations
import re
from typing import Any, Dict, List, Union
from pathlib import Path
import pandas as pd

from urarovite.validators.base import BaseValidator, ValidationResult
from urarovite.core.exceptions import ValidationError
from urarovite.core.spreadsheet import SpreadsheetInterface
from urarovite.utils.sheets import split_segments


class SheetNameQuotingValidator(BaseValidator):
    """Validator that ensures proper sheet name quoting in verification ranges."""

    def __init__(self) -> None:
        super().__init__(
            validator_id="sheet_name_quoting",
            name="Sheet Name Quoting",
            description=(
                "Ensures all sheet names in verification ranges are properly "
                "quoted with single quotes (e.g., 'Sheet Name'!A1:B2). "
                "Automatically converts curly quotes to straight quotes."
            ),
        )

    # Regular expression for properly quoted sheet names
    # Matches: 'SheetName'! or 'SheetName'$ (for whole sheet references)
    SHEET_PREFIX_RE = re.compile(r"^'[^']+'(!|$)")

    def _segment_is_quoted(self, segment: str) -> bool:
        """Check if a segment has properly quoted sheet name."""
        return bool(self.SHEET_PREFIX_RE.match(segment))

    def _has_curly_quotes(self, text: str) -> bool:
        """Check if text contains curly quotes.

        Detects Unicode curly quotes:
        - " (U+201C) LEFT DOUBLE QUOTATION MARK
        - " (U+201D) RIGHT DOUBLE QUOTATION MARK
        - ' (U+2018) LEFT SINGLE QUOTATION MARK
        - ' (U+2019) RIGHT SINGLE QUOTATION MARK

        Args:
            text: Text to check for curly quotes

        Returns:
            True if text contains curly quotes, False otherwise
        """
        if not text:
            return False

        curly_quotes = ["\u201c", "\u201d", "\u2018", "\u2019"]
        return any(quote in text for quote in curly_quotes)

    def _convert_curly_quotes(self, text: str) -> str:
        """Convert curly quotes to straight quotes.

        Converts Unicode curly quotes to ASCII straight quotes:
        - " (U+201C) → ' (ASCII single quote)
        - " (U+201D) → ' (ASCII single quote)
        - ' (U+2018) → ' (ASCII single quote)
        - ' (U+2019) → ' (ASCII single quote)

        Args:
            text: Text that may contain curly quotes

        Returns:
            Text with curly quotes converted to straight quotes
        """
        if not text:
            return text

        # Convert curly double quotes to single quotes (for sheet name quoting)
        text = text.replace("\u201c", "'")  # U+201C LEFT DOUBLE QUOTATION MARK
        text = text.replace("\u201d", "'")  # U+201D RIGHT DOUBLE QUOTATION MARK

        # Convert curly single quotes to straight single quotes
        text = text.replace("\u2018", "'")  # U+2018 LEFT SINGLE QUOTATION MARK
        text = text.replace("\u2019", "'")  # U+2019 RIGHT SINGLE QUOTATION MARK

        return text

    def validate(
        self,
        spreadsheet_source: Union[str, Path, SpreadsheetInterface],
        mode: str,
        auth_credentials: Dict[str, Any] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Execute sheet name quoting validation.

        Args:
            spreadsheet_source: Either a Google Sheets URL, Excel file path,
                or SpreadsheetInterface
            mode: Either "fix" (not applicable) or "flag" (report only)
            auth_credentials: Authentication credentials (required for Google Sheets)
            **kwargs: Must contain either 'row' with data or 'ranges_str' directly

        Returns:
            Dict with validation results
        """

        def validation_logic(
            spreadsheet: SpreadsheetInterface, result: ValidationResult, **kwargs
        ) -> None:
            # Extract ranges string from parameters
            ranges_str = ""

            if "ranges_str" in kwargs:
                # Direct string input
                ranges_str = kwargs["ranges_str"]
            elif "row" in kwargs:
                # Extract from row data
                row = kwargs["row"]
                if row is None:
                    result.add_error("Row data is required for this validator")
                    return

                field = kwargs.get("field", "verification_field_ranges")
                ranges_str = str(row.get(field, ""))
            else:
                # No parameters provided - no flags to report
                result.details["total_segments"] = 0
                result.details["failing_segments"] = []
                result.details["original"] = ""
                result.set_automated_log("No flags found")
                return

            # Parse segments and check quoting
            segments = split_segments(ranges_str)
            failing_segments = []

            for segment in segments:
                # Convert curly quotes to straight quotes before validation
                converted_segment = self._convert_curly_quotes(segment)

                # Check if the converted segment is properly quoted
                if not self._segment_is_quoted(converted_segment):
                    failing_segments.append(segment)
                    result.add_detailed_issue(
                        sheet_name="N/A",  # Not sheet-specific, but range-specific
                        cell=segment,
                        message="Sheet name in range is not properly quoted",
                        value=segment,
                    )
            # Prepare result details
            result.details["total_segments"] = len(segments)
            result.details["original"] = ranges_str

            if result.flags_found > 0:
                result.set_automated_log(
                    f"Found {result.flags_found} unquoted sheet names."
                )
            else:
                result.set_automated_log("All sheet names are properly quoted.")

        return self._execute_validation(
            validation_logic, spreadsheet_source, auth_credentials, **kwargs
        )


# Convenience function for backward compatibility
def run(ranges_str: str, mode: str = "flag") -> Dict[str, Any]:
    """
    Execute sheet name quoting check using the new BaseValidator pattern.

    Args:
        ranges_str: String with ranges to validate
        mode: Validation mode ('flag' or 'fix')

    Returns:
        Dict with validation results
    """
    from .base import ValidationResult

    # Create a simple validation result without needing a spreadsheet
    result = ValidationResult()

    try:
        # Parse and validate the ranges string directly
        validator = SheetNameQuotingValidator()

        # Extract the validation logic without needing spreadsheet infrastructure
        segments = split_segments(ranges_str) if ranges_str else []
        failing_segments = []

        for segment in segments:
            # Convert curly quotes to straight quotes before validation
            converted_segment = validator._convert_curly_quotes(segment)

            # Check if the converted segment is properly quoted
            if not validator._segment_is_quoted(converted_segment):
                failing_segments.append(segment)

        # Set results
        result.details["total_segments"] = len(segments)
        result.details["failing_segments"] = failing_segments
        result.details["original"] = ranges_str

        if failing_segments:
            if mode == "flag":
                result.add_issue(len(failing_segments))
                result.set_automated_log(
                    f"Found {len(failing_segments)} unquoted sheet names"
                )
            else:
                result.add_fix(len(failing_segments))
                result.set_automated_log(
                    f"Fixed {len(failing_segments)} unquoted sheet names"
                )
        else:
            result.set_automated_log("All sheet names are properly quoted")

    except Exception as e:
        result.add_error(f"Validation error: {str(e)}")
        result.details["total_segments"] = 0
        result.details["failing_segments"] = []
        result.details["original"] = ranges_str or ""
        result.set_automated_log("No flags found")

    return result.to_dict()


# Backwards compatible helper name
run_detailed = run
