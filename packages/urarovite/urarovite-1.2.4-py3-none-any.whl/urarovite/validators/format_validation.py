"""Format validation validators.

This module implements validators for checking and fixing verification ranges.
"""

import re
from typing import Any, Dict, List, Union
from pathlib import Path

from urarovite.validators.base import BaseValidator, ValidationResult
from urarovite.core.exceptions import ValidationError
from urarovite.core.spreadsheet import SpreadsheetInterface
from urarovite.validators.sheet_name_quoting import run as validate_sheet_name_quoting


class VerificationRangesValidator(BaseValidator):
    """Validator for verification ranges."""

    def __init__(self) -> None:
        super().__init__(
            validator_id="invalid_verification_ranges",
            name="Validate Verification Ranges",
            description="Validates verification ranges for proper A1 notation, @@ separators, and quoted tab names. Automatically converts curly quotes to straight quotes.",
        )

    def validate(
        self,
        spreadsheet_source: Union[str, Path, SpreadsheetInterface],
        mode: str,
        auth_credentials: Dict[str, Any] = None,
        verification_ranges_columns: List[int] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Validate verification ranges in specified columns.

        Validates and optionally fixes verification ranges by:
        - Converting curly quotes (" " ' ') to straight quotes (')
        - Ensuring proper sheet name quoting with single quotes
        - Validating A1 notation format
        - Checking @@ separator usage

        Args:
            spreadsheet_source: Either a Google Sheets URL, Excel file path,
                or SpreadsheetInterface
            mode: Either "fix" (auto-quote tabs, fix separators, convert curly quotes) or "flag" (report only)
            auth_credentials: Authentication credentials (required for Google Sheets)
            verification_ranges_columns: List of 1-based column indices containing verification ranges

        Returns:
            Dict with validation results
        """
        result = ValidationResult()
        spreadsheet = None

        try:
            # Get spreadsheet interface
            spreadsheet = self._get_spreadsheet(
                spreadsheet_source, auth_credentials, read_only=mode != "fix"
            )

            # Get all sheet data
            data, sheet_name = self._get_all_sheet_data(spreadsheet)

            if not data:
                result.add_error("Sheet is empty - no data to validate")
                result.set_automated_log("Sheet is empty - no data to validate")
                return result.to_dict()

            # Auto-detect verification ranges columns if not specified
            if verification_ranges_columns is None:
                verification_ranges_columns = self._detect_verification_ranges_columns(
                    data
                )

            fixed_data = []

            # Check and optionally fix verification ranges
            for row_idx, row in enumerate(data):
                fixed_row = list(row)

                for col_idx in verification_ranges_columns:
                    col_zero_based = col_idx - 1

                    if col_zero_based < len(row) and row[col_zero_based]:
                        ranges_str = str(row[col_zero_based]).strip()

                        if ranges_str:
                            validation_result = self._validate_ranges(ranges_str)

                            if not validation_result["ok"]:
                                cell_ref = self._generate_cell_reference(
                                    row_idx, col_zero_based, sheet_name
                                )
                                failing_segments_info = f"Failing segments: {validation_result['failing_segments']}"

                                if mode == "fix":
                                    # Try to fix the ranges
                                    fixed_ranges = self._fix_ranges(ranges_str)
                                    if fixed_ranges != ranges_str:
                                        fixed_row[col_zero_based] = fixed_ranges
                                        result.add_detailed_fix(
                                            sheet_name=sheet_name,
                                            cell=cell_ref,
                                            message=f"Fixed verification range. {failing_segments_info}",
                                            old_value=ranges_str,
                                            new_value=fixed_ranges,
                                        )
                                    else:
                                        result.add_detailed_issue(
                                            sheet_name=sheet_name,
                                            cell=cell_ref,
                                            message=f"Cannot auto-fix verification range. {failing_segments_info}",
                                            value=ranges_str,
                                        )
                                else:
                                    result.add_detailed_issue(
                                        sheet_name=sheet_name,
                                        cell=cell_ref,
                                        message=f"Invalid verification range format. {failing_segments_info}",
                                        value=ranges_str,
                                    )

                fixed_data.append(fixed_row)

            # If fixes were applied, update the sheet
            if mode == "fix" and result.fixes_applied > 0:
                self._update_sheet_data(spreadsheet, sheet_name, fixed_data)
                spreadsheet.save()

            # Set a summary log message
            if result.fixes_applied > 0 and result.flags_found > 0:
                result.set_automated_log(
                    f"Applied {result.fixes_applied} fixes and found {result.flags_found} "
                    f"unfixable flags."
                )
            elif result.fixes_applied > 0:
                result.set_automated_log(f"Applied {result.fixes_applied} fixes.")
            elif result.flags_found > 0:
                result.set_automated_log(f"Found {result.flags_found} flags.")
            else:
                result.set_automated_log("No flags found")

        except ValidationError:
            raise
        except Exception as e:
            result.add_error(f"Unexpected error: {str(e)}")
        finally:
            # Clean up resources
            if spreadsheet:
                try:
                    spreadsheet.close()
                except Exception:
                    pass  # Ignore cleanup errors

        return result.to_dict()

    def _validate_ranges(self, ranges_str: str) -> Dict[str, Any]:
        """Validate verification ranges using sheet name quoting validator."""
        result = validate_sheet_name_quoting(ranges_str)
        # Convert ValidationResult format to old format for backward compatibility
        return {
            "ok": result["flags_found"] == 0,
            "failing_segments": result["details"].get("failing_segments", []),
            "total_segments": result["details"].get("total_segments", 0),
            "original": result["details"].get("original", ranges_str),
        }

    def _fix_ranges(self, ranges_str: str) -> str:
        """Fix common flags in verification ranges."""
        # First, convert any curly quotes to straight quotes
        ranges_str = self._convert_curly_quotes(ranges_str)

        # Split by @@ and clean up segments
        segments = [s.strip() for s in ranges_str.split("@@") if s.strip()]
        fixed_segments = []

        for segment in segments:
            fixed_segment = self._fix_segment(segment)
            fixed_segments.append(fixed_segment)

        return "@@".join(fixed_segments)

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

    def _fix_segment(self, segment: str) -> str:
        """Fix a single range segment."""
        segment = segment.strip()

        # Convert curly quotes to straight quotes first
        segment = self._convert_curly_quotes(segment)

        # If segment already starts with a quoted sheet name, return as-is
        if re.match(r"^'[^']+'!", segment):
            return segment

        # Check if there's an exclamation mark (sheet!range format)
        if "!" in segment:
            sheet_part, range_part = segment.split("!", 1)
            sheet_part = sheet_part.strip()
            range_part = range_part.strip()

            # Check if sheet name is already properly quoted after curly quote conversion
            if sheet_part.startswith("'") and sheet_part.endswith("'"):
                # Already properly quoted, just return
                return f"{sheet_part}!{range_part}"

            # Remove malformed quotes if present
            if sheet_part.startswith("'") and not sheet_part.endswith("'"):
                sheet_part = sheet_part[1:]
            elif sheet_part.endswith("'") and not sheet_part.startswith("'"):
                sheet_part = sheet_part[:-1]

            # Quote the sheet name for consistency
            return f"'{sheet_part}'!{range_part}"
        else:
            # Whole sheet reference
            # Check if already properly quoted after curly quote conversion
            if segment.startswith("'") and segment.endswith("'"):
                return segment

            # Remove malformed quotes if present
            if segment.startswith("'") and not segment.endswith("'"):
                segment = segment[1:]
            elif segment.endswith("'") and not segment.startswith("'"):
                segment = segment[:-1]

            # Quote the whole sheet reference
            return f"'{segment}'"

    def _needs_quoting(self, sheet_name: str) -> bool:
        """Check if a sheet name needs quoting (has spaces or special characters)."""
        # According to the spec, we want to quote all sheet names for consistency
        # but especially those with spaces or non-alphanumeric characters
        return not re.match(r"^[a-zA-Z0-9_]+$", sheet_name)

    def _detect_verification_ranges_columns(self, data: List[List[Any]]) -> List[int]:
        """Auto-detect columns that likely contain verification ranges."""
        verification_ranges_columns = []

        if not data:
            return verification_ranges_columns

        # Check first few rows for verification ranges
        sample_rows = data[: min(10, len(data))]

        for col_idx in range(len(data[0]) if data else 0):
            verification_count = 0
            total_non_empty = 0

            for row in sample_rows:
                if col_idx < len(row) and row[col_idx]:
                    total_non_empty += 1
                    ranges_str = str(row[col_idx]).strip()
                    if self._looks_like_verification_range(ranges_str):
                        verification_count += 1

            # If more than 50% of non-empty cells look like verification ranges, include this column
            if total_non_empty > 0 and verification_count / total_non_empty > 0.5:
                verification_ranges_columns.append(col_idx + 1)  # Convert to 1-based

        return verification_ranges_columns

    def _looks_like_verification_range(self, ranges_str: str) -> bool:
        """Check if a string looks like a verification range."""
        if not ranges_str:
            return False

        # Look for patterns that suggest A1 notation ranges
        # - Contains letters followed by numbers (A1, B2, etc.)
        # - Contains exclamation marks (sheet references)
        # - Contains @@ separators
        # - Contains colons (range separators)
        patterns = [
            r"[A-Z]+\d+",  # A1 notation
            r"!",  # Sheet reference
            r"@@",  # Segment separator
            r"[A-Z]+\d+:[A-Z]+\d+",  # Range notation
        ]

        return any(re.search(pattern, ranges_str) for pattern in patterns)
