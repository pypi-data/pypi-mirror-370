"""Data quality validators for common spreadsheet flags.

This module implements validators for basic data quality flags such as
empty cells, duplicate rows, and inconsistent formatting.
"""

import hashlib
import re
from typing import Any, Dict, List, Set, Union
from pathlib import Path

from urarovite.validators.base import BaseValidator, ValidationResult
from urarovite.core.exceptions import ValidationError
from urarovite.core.spreadsheet import SpreadsheetInterface

ILLEGAL_CHARS = ["\\", "/", "?", "*", "[", "]"]

# Excel's maximum tab name length
EXCEL_MAX_TAB_NAME_LENGTH = 31
# Length of collision suffix including separator (e.g., "_AB12")
COLLISION_SUFFIX_LENGTH = 5
# Maximum length for the base name after accounting for collision suffix
MAX_BASE_NAME_LENGTH = EXCEL_MAX_TAB_NAME_LENGTH - COLLISION_SUFFIX_LENGTH


class TabNameValidator(BaseValidator):
    """Validator for checking and fixing tab names."""

    def __init__(self) -> None:
        super().__init__(
            validator_id="tab_names",
            name="Fix Tab Names",
            description="Validates tab names for illegal characters and Excel length limits (31 chars). Fixes illegal characters and truncates long names with collision-safe suffixes.",
        )

    def validate(
        self,
        spreadsheet_source: Union[str, Path, SpreadsheetInterface],
        mode: str,
        auth_credentials: Dict[str, Any] = None,
        replacement_char: str = "_",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Check for and optionally fix tab name characters.

        Args:
            spreadsheet_source: Either a Google Sheets URL, Excel file path,
                or SpreadsheetInterface
            mode: Either "fix" (fix tab names) or "flag" (report only)
            auth_credentials: Authentication credentials (required for Google Sheets)
            replacement_char: Character to replace illegal characters with (default: "_")

        Returns:
            Dict with validation results including mapping of changes
        """

        def validation_logic(
            spreadsheet: SpreadsheetInterface, result: ValidationResult, **kwargs
        ) -> None:
            # Get spreadsheet metadata to access tab information
            metadata = spreadsheet.get_metadata()
            sheet_names = metadata.sheet_names

            if not sheet_names:
                result.add_error("No sheets found in spreadsheet")
                result.set_automated_log("No flags found")
                return

            # Collect all existing tab names for collision detection
            all_tab_names = set(sheet_names)

            tab_flags = []
            name_mapping = {}
            used_names = set(
                all_tab_names
            )  # Track all names (original + new) to avoid collisions

            # Check each tab for illegal characters and length violations
            for tab_name in sheet_names:
                # Check for illegal characters: \ / ? * [ ]
                has_illegal_chars = any(char in tab_name for char in ILLEGAL_CHARS)

                # Check for Excel length violation (>31 characters)
                exceeds_excel_limit = len(tab_name) > EXCEL_MAX_TAB_NAME_LENGTH

                if has_illegal_chars or exceeds_excel_limit:
                    # Start with the original name
                    fixed_name = tab_name

                    # First, clean illegal characters if present
                    if has_illegal_chars:
                        fixed_name = self._clean_tab_name(fixed_name, replacement_char)

                    # Then, handle Excel length limit if exceeded
                    if len(fixed_name) > EXCEL_MAX_TAB_NAME_LENGTH:
                        fixed_name = self._truncate_for_excel(fixed_name, used_names)

                    # Handle collisions by appending numbers (if not already handled by truncation)
                    final_name = self._resolve_name_collision(fixed_name, used_names)

                    # Add to used names to prevent future collisions
                    used_names.add(final_name)

                    # Create mapping entry
                    name_mapping[tab_name] = final_name

                    # Record detected flags
                    detected_chars = (
                        [char for char in ILLEGAL_CHARS if char in tab_name]
                        if has_illegal_chars
                        else []
                    )

                    issue_types = []
                    if has_illegal_chars:
                        issue_types.append("illegal_characters")
                    if exceeds_excel_limit:
                        issue_types.append("excel_length_limit")

                    tab_flags.append(
                        {
                            "original_name": tab_name,
                            "fixed_name": final_name,
                            "original_length": len(tab_name),
                            "fixed_length": len(final_name),
                            "illegal_chars": detected_chars,
                            "issue_types": issue_types,
                        }
                    )

            # Record results
            if tab_flags:
                if mode == "fix":
                    # Update tab names
                    for issue in tab_flags:
                        spreadsheet.update_sheet_properties(
                            sheet_name=issue["original_name"],
                            new_name=issue["fixed_name"],
                        )

                    # Save changes (important for Excel files)
                    spreadsheet.save()

                    result.add_fix(len(tab_flags))
                    result.details["fixed_tabs"] = tab_flags
                    result.details["name_mapping"] = name_mapping
                    result.set_automated_log(f"Fixed tab names: {tab_flags}")
                else:
                    result.add_issue(len(tab_flags))
                    result.details["tab_flags"] = tab_flags
                    result.details["proposed_mapping"] = name_mapping
                    result.set_automated_log(f"Tab name flags found: {tab_flags}")
            else:
                result.set_automated_log("No flags found")

        return self._execute_validation(
            validation_logic,
            spreadsheet_source,
            auth_credentials,
            replacement_char=replacement_char,
            **kwargs,
        )

    def _clean_tab_name(self, tab_name: str, replacement_char: str) -> str:
        """Clean a tab name by replacing illegal characters.

        Args:
            tab_name: Original tab name
            replacement_char: Character to replace illegal characters with

        Returns:
            Cleaned tab name
        """
        fixed_name = tab_name

        # Replace each illegal character with replacement character
        for char in ILLEGAL_CHARS:
            fixed_name = fixed_name.replace(char, replacement_char)

        # Remove multiple consecutive replacement characters
        fixed_name = re.sub(
            f"{re.escape(replacement_char)}+", replacement_char, fixed_name
        )

        # Remove leading/trailing replacement characters
        fixed_name = fixed_name.strip(replacement_char)

        # Ensure name isn't empty
        if not fixed_name:
            fixed_name = "Sheet"

        return fixed_name

    def _resolve_name_collision(self, proposed_name: str, used_names: Set[str]) -> str:
        """Resolve name collisions by appending numbers.

        Args:
            proposed_name: The proposed cleaned name
            used_names: Set of already used names

        Returns:
            Final name that doesn't collide with existing names
        """
        if proposed_name not in used_names:
            return proposed_name

        # Try appending numbers until we find an unused name
        counter = 1
        while f"{proposed_name}_{counter}" in used_names:
            counter += 1

        return f"{proposed_name}_{counter}"

    def _truncate_for_excel(self, tab_name: str, used_names: Set[str]) -> str:
        """Truncate tab name to Excel's 31-character limit with collision-safe suffix.

        Args:
            tab_name: The tab name that exceeds Excel's limit
            used_names: Set of already used names to avoid collisions

        Returns:
            Truncated name with collision suffix if needed
        """
        # First, try simple truncation
        if len(tab_name) <= EXCEL_MAX_TAB_NAME_LENGTH:
            return tab_name

        simple_truncated = tab_name[:EXCEL_MAX_TAB_NAME_LENGTH]

        if simple_truncated not in used_names:
            return simple_truncated

        # If there's a collision, create a collision-safe version
        # Truncate to leave room for collision suffix
        truncated_base = tab_name[:MAX_BASE_NAME_LENGTH]

        # Generate a short hash from the original name for uniqueness
        hash_suffix = self._generate_collision_suffix(tab_name)

        candidate = f"{truncated_base}_{hash_suffix}"

        # If somehow this still collides (very unlikely), add a counter
        counter = 1
        while candidate in used_names:
            # For counters 1-9, we need 1 extra char; for 10-99, we need 2 extra chars
            counter_str = str(counter)
            needed_space = len(counter_str)

            # Adjust the base to make room for counter (preserve underscore and partial suffix)
            adjusted_base = tab_name[
                : EXCEL_MAX_TAB_NAME_LENGTH - 1 - len(hash_suffix) - needed_space
            ]
            candidate = f"{adjusted_base}_{hash_suffix}{counter}"
            counter += 1
            if counter > 99:  # Safeguard against infinite loop
                break

        return candidate

    def _generate_collision_suffix(self, original_name: str) -> str:
        """Generate a 4-character collision suffix from the original name.

        Args:
            original_name: The original tab name

        Returns:
            4-character suffix (e.g., "AB12")
        """
        # Create a hash of the original name
        hash_obj = hashlib.md5(original_name.encode("utf-8"))
        hash_hex = hash_obj.hexdigest()

        # Take first 4 characters and convert to uppercase for readability
        return hash_hex[:4].upper()


class EmptyCellsValidator(BaseValidator):
    """Validator for identifying and fixing empty cells."""

    def __init__(self) -> None:
        super().__init__(
            validator_id="empty_cells",
            name="Fix Empty Cells",
            description="Identifies and optionally fills empty cells with default values. Supports targeting specific cell ranges.",
        )

    def validate(
        self,
        spreadsheet_source: Union[str, Path, SpreadsheetInterface],
        mode: str,
        auth_credentials: Dict[str, Any] = None,
        fill_value: str = "",
        target_ranges: Union[str, List[str], None] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Check for and optionally fix empty cells.

        Args:
            spreadsheet_source: Either a Google Sheets URL, Excel file path,
                or SpreadsheetInterface
            mode: Either "fix" (fill empty cells) or "flag" (report only)
            auth_credentials: Authentication credentials (required for Google Sheets)
            fill_value: Value to use when filling empty cells (default: "")
            target_ranges: Specific ranges to check. Can be:
                - None: Check all cells (default behavior)
                - String: Single range (e.g., 'Case'!D72:D76)
                - List: Multiple ranges (e.g., ['Case'!D72, 'Case'!D73, 'Case'!D74])
                Range formats: 'Sheet'!A1:B10 or 'Sheet'!A1, 'Sheet'!B2

        Returns:
            Dict with validation results
        """
        result = ValidationResult()
        spreadsheet = None

        try:
            # Get spreadsheet interface - determine read_only based on mode
            read_only = mode != "fix"  # False for fix mode, True for flag mode
            spreadsheet = self._get_spreadsheet(
                spreadsheet_source, auth_credentials, read_only=read_only
            )

            # Get all sheet data and sheet name
            data, sheet_name = self._get_all_sheet_data(spreadsheet)

            if not data:
                result.details["message"] = "No data found to validate"
                result.set_automated_log("No data found to validate")
                return result.to_dict()

            # Parse target ranges if specified
            target_cells = (
                self._parse_target_ranges(target_ranges, sheet_name)
                if target_ranges
                else None
            )

            empty_cells = []
            fixed_data = []

            # Determine the maximum number of columns across all rows
            max_cols = max(len(row) for row in data) if data else 0

            # Check each row for empty cells
            for row_idx, row in enumerate(data):
                fixed_row = []
                # Extend row to max_cols length if needed
                extended_row = row + [""] * (max_cols - len(row))

                for col_idx, cell in enumerate(extended_row):
                    # Check if this cell should be validated based on target_ranges
                    should_check = True
                    if target_cells is not None:
                        cell_pos = (row_idx + 1, col_idx + 1)  # 1-based indexing
                        should_check = cell_pos in target_cells

                    if should_check and (cell == "" or cell is None):
                        empty_cells.append(
                            (row_idx + 1, col_idx + 1)
                        )  # 1-based indexing
                        if mode == "fix":
                            fixed_row.append(fill_value)
                        else:
                            fixed_row.append(cell)
                    else:
                        fixed_row.append(cell)
                fixed_data.append(fixed_row)

            # Record results
            if empty_cells:
                if mode == "fix":
                    # Update the sheet with fixed data
                    self._update_sheet_data(spreadsheet, sheet_name, fixed_data)

                    # Save changes (important for Excel files)
                    spreadsheet.save()

                    result.add_fix(len(empty_cells))
                    result.details["fixed_cells"] = empty_cells
                    result.set_automated_log(
                        f"Fixed empty cells at positions: {empty_cells}"
                    )
                else:
                    result.add_issue(len(empty_cells))
                    result.details["empty_cells"] = empty_cells
                    result.set_automated_log(
                        f"Empty cells found at positions: {empty_cells}"
                    )
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

    def _parse_target_ranges(
        self, target_ranges: Union[str, List[str], None], default_sheet: str
    ) -> Set[tuple[int, int]]:
        """Parse target ranges into a set of cell positions.

        Args:
            target_ranges: Range specification(s) to parse
            default_sheet: Default sheet name if not specified in range

        Returns:
            Set of (row, col) tuples representing target cell positions (1-based)

        Raises:
            ValidationError: If range format is invalid
        """
        if target_ranges is None:
            return set()

        # Convert single string to list for uniform processing
        if isinstance(target_ranges, str):
            target_ranges = [target_ranges]

        target_cells = set()

        for range_spec in target_ranges:
            if not isinstance(range_spec, str):
                raise ValidationError(f"Invalid range specification: {range_spec}")

            # Parse the range specification
            cells = self._parse_single_range(range_spec.strip(), default_sheet)
            target_cells.update(cells)

        return target_cells

    def _parse_single_range(
        self, range_spec: str, default_sheet: str
    ) -> Set[tuple[int, int]]:
        """Parse a single range specification into cell positions.

        Args:
            range_spec: Single range specification (e.g., 'Sheet'!A1:B10, 'Sheet'!A1)
            default_sheet: Default sheet name if not specified

        Returns:
            Set of (row, col) tuples representing cell positions (1-based)

        Raises:
            ValidationError: If range format is invalid
        """
        # Extract sheet name and range part
        if "!" in range_spec:
            sheet_name, range_part = range_spec.split("!", 1)
            sheet_name = sheet_name.strip().strip("'\"")  # Remove quotes
            range_part = range_part.strip()
        else:
            sheet_name = default_sheet
            range_part = range_spec.strip()

        # Check if sheet name matches (case-insensitive for backward compatibility)
        if sheet_name.lower() != default_sheet.lower():
            raise ValidationError(
                f"Sheet '{sheet_name}' not found. Available sheet: '{default_sheet}'"
            )

        cells = set()

        # Check if it's a range (contains ':')
        if ":" in range_part:
            # Range format: A1:B10
            start_cell, end_cell = range_part.split(":", 1)
            start_pos = self._parse_cell_reference(start_cell.strip())
            end_pos = self._parse_cell_reference(end_cell.strip())

            # Add all cells in the range
            for row in range(start_pos[0], end_pos[0] + 1):
                for col in range(start_pos[1], end_pos[1] + 1):
                    cells.add((row, col))
        else:
            # Single cell format: A1
            cell_pos = self._parse_cell_reference(range_part)
            cells.add(cell_pos)

        return cells

    def _parse_cell_reference(self, cell_ref: str) -> tuple[int, int]:
        """Parse cell reference like 'A1' into row/column indices.

        Args:
            cell_ref: Cell reference (e.g., 'A1', 'Z100')

        Returns:
            Tuple of (row, col) - both 1-based

        Raises:
            ValidationError: If cell reference format is invalid
        """
        import re

        try:
            # Use regex to split column letters and row numbers
            match = re.match(r"^([A-Z]+)(\d+)$", cell_ref.upper())
            if not match:
                raise ValidationError(f"Invalid cell reference: {cell_ref}")

            col_letters, row_str = match.groups()

            # Convert column letters to index
            col_idx = self._column_letters_to_index(col_letters)
            row_idx = int(row_str)

            return row_idx, col_idx

        except Exception as e:
            raise ValidationError(f"Invalid cell reference '{cell_ref}': {str(e)}")

    def _column_letters_to_index(self, letters: str) -> int:
        """Convert Excel column letters to 1-based index.

        Args:
            letters: Column letters (e.g., 'A', 'Z', 'AA')

        Returns:
            1-based column index
        """
        result = 0
        for letter in letters:
            result = result * 26 + (ord(letter.upper()) - ord("A") + 1)
        return result


class DuplicateRowsValidator(BaseValidator):
    """Validator for identifying and removing duplicate rows."""

    def __init__(self) -> None:
        super().__init__(
            validator_id="duplicate_rows",
            name="Remove Duplicate Rows",
            description="Finds and optionally removes duplicate rows based on all columns",
        )

    def validate(
        self,
        spreadsheet_source: Union[str, Path, SpreadsheetInterface],
        mode: str,
        auth_credentials: Dict[str, Any] = None,
        keep_first: bool = True,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Check for and optionally remove duplicate rows.

        Args:
            spreadsheet_source: Either a Google Sheets URL, Excel file path,
                or SpreadsheetInterface
            mode: Either "fix" (remove duplicates) or "flag" (report only)
            auth_credentials: Authentication credentials (required for Google Sheets)
            keep_first: If True, keep first occurrence of duplicate (default: True)

        Returns:
            Dict with validation results
        """
        result = ValidationResult()
        spreadsheet = None

        try:
            # Get spreadsheet interface - determine read_only based on mode
            read_only = mode != "fix"  # False for fix mode, True for flag mode
            spreadsheet = self._get_spreadsheet(
                spreadsheet_source, auth_credentials, read_only=read_only
            )

            # Get all sheet data and sheet name
            data, sheet_name = self._get_all_sheet_data(spreadsheet)

            if not data:
                result.details["message"] = "No data found to validate"
                result.set_automated_log("No data found to validate")
                return result.to_dict()

            # Find duplicates
            seen_rows: Set[str] = set()
            duplicate_indices: List[int] = []
            unique_data: List[List[Any]] = []

            for row_idx, row in enumerate(data):
                # Convert row to string for comparison (handle None values)
                row_str = str([cell if cell is not None else "" for cell in row])

                if row_str in seen_rows:
                    duplicate_indices.append(row_idx + 1)  # 1-based indexing
                    if mode == "fix":
                        # Skip duplicate row (keep_first=True means skip duplicates)
                        continue
                else:
                    seen_rows.add(row_str)

                if mode == "fix":
                    unique_data.append(row)

            # Record results
            if duplicate_indices:
                if mode == "fix":
                    # Update the sheet with deduplicated data
                    self._update_sheet_data(spreadsheet, sheet_name, unique_data)

                    # Save changes (important for Excel files)
                    spreadsheet.save()

                    result.add_fix(len(duplicate_indices))
                    result.details["removed_rows"] = duplicate_indices
                    result.set_automated_log(
                        f"Removed duplicate rows: {duplicate_indices}"
                    )
                else:
                    result.add_issue(len(duplicate_indices))
                    result.details["duplicate_rows"] = duplicate_indices
                    result.set_automated_log(
                        f"Duplicate rows found: {duplicate_indices}"
                    )
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


class InconsistentFormattingValidator(BaseValidator):
    """Validator for fixing inconsistent text formatting."""

    def __init__(self) -> None:
        super().__init__(
            validator_id="inconsistent_formatting",
            name="Fix Inconsistent Formatting",
            description="Standardizes text formatting (case, whitespace, etc.)",
        )

    def validate(
        self,
        spreadsheet_source: Union[str, Path, SpreadsheetInterface],
        mode: str,
        auth_credentials: Dict[str, Any] = None,
        trim_whitespace: bool = True,
        standardize_case: str = None,  # "upper", "lower", "title", or None
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Check for and optionally fix inconsistent formatting.

        Args:
            spreadsheet_source: Either a Google Sheets URL, Excel file path,
                or SpreadsheetInterface
            mode: Either "fix" (standardize formatting) or "flag" (report only)
            auth_credentials: Authentication credentials (required for Google Sheets)
            trim_whitespace: Whether to trim leading/trailing whitespace
            standardize_case: Case standardization ("upper", "lower", "title", or None)

        Returns:
            Dict with validation results
        """
        result = ValidationResult()
        spreadsheet = None

        try:
            # Get spreadsheet interface - determine read_only based on mode
            read_only = mode != "fix"  # False for fix mode, True for flag mode
            spreadsheet = self._get_spreadsheet(
                spreadsheet_source, auth_credentials, read_only=read_only
            )

            # Get all sheet data
            data, sheet_name = self._get_all_sheet_data(spreadsheet)

            if not data:
                result.details["message"] = "No data found to validate"
                result.set_automated_log("No data found to validate")
                return result.to_dict()

            formatting_flags = []
            fixed_data = []

            # Check and fix formatting flags
            for row_idx, row in enumerate(data):
                fixed_row = []
                for col_idx, cell in enumerate(row):
                    original_cell = cell
                    fixed_cell = cell

                    # Only process string values
                    if isinstance(cell, str):
                        # Trim whitespace
                        if trim_whitespace:
                            fixed_cell = fixed_cell.strip()

                        # Standardize case
                        if standardize_case == "upper":
                            fixed_cell = fixed_cell.upper()
                        elif standardize_case == "lower":
                            fixed_cell = fixed_cell.lower()
                        elif standardize_case == "title":
                            fixed_cell = fixed_cell.title()

                        # Remove extra whitespace between words
                        fixed_cell = re.sub(r"\s+", " ", fixed_cell)

                        # Record if changes were made
                        if original_cell != fixed_cell:
                            formatting_flags.append(
                                {
                                    "row": row_idx + 1,
                                    "col": col_idx + 1,
                                    "original": original_cell,
                                    "fixed": fixed_cell,
                                }
                            )

                    fixed_row.append(fixed_cell)
                fixed_data.append(fixed_row)

            # Record results
            if formatting_flags:
                if mode == "fix":
                    # Update the sheet with fixed data
                    self._update_sheet_data(spreadsheet, sheet_name, fixed_data)

                    # Save changes (important for Excel files)
                    spreadsheet.save()

                    result.add_fix(len(formatting_flags))
                    result.details["fixed_formatting"] = formatting_flags
                    result.set_automated_log(
                        f"Fixed formatting flags: {len(formatting_flags)} cells"
                    )
                else:
                    result.add_issue(len(formatting_flags))
                    result.details["formatting_flags"] = formatting_flags
                    result.set_automated_log(
                        f"Formatting inconsistencies found: {len(formatting_flags)} cells"
                    )
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


class MissingRequiredFieldsValidator(BaseValidator):
    """Validator for checking required fields."""

    def __init__(self) -> None:
        super().__init__(
            validator_id="missing_required_fields",
            name="Check Required Fields",
            description="Validates that required fields are not empty",
        )

    def validate(
        self,
        spreadsheet_source: Union[str, Path, SpreadsheetInterface],
        mode: str,
        auth_credentials: Dict[str, Any] = None,
        required_columns: List[int] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Check for missing required fields.

        Args:
            spreadsheet_source: Either a Google Sheets URL, Excel file path,
                or SpreadsheetInterface
            mode: Either "fix" (not applicable) or "flag" (report only)
            auth_credentials: Authentication credentials (required for Google Sheets)
            required_columns: List of 1-based column indices that are required

        Returns:
            Dict with validation results
        """
        result = ValidationResult()
        spreadsheet = None

        try:
            # Get spreadsheet interface - determine read_only based on mode
            read_only = mode != "fix"  # False for fix mode, True for flag mode
            spreadsheet = self._get_spreadsheet(
                spreadsheet_source, auth_credentials, read_only=read_only
            )

            # Get all sheet data
            data, sheet_name = self._get_all_sheet_data(spreadsheet)

            if not data:
                result.details["message"] = "No data found to validate"
                result.set_automated_log("No data found to validate")
                return result.to_dict()

            # Default to checking all columns if none specified
            if required_columns is None:
                required_columns = list(range(1, len(data[0]) + 1)) if data else []

            missing_fields = []

            # Check each row for missing required fields
            for row_idx, row in enumerate(data):
                for col_idx in required_columns:
                    # Convert to 0-based index
                    col_zero_based = col_idx - 1

                    # Check if column exists and has value
                    if (
                        col_zero_based >= len(row)
                        or row[col_zero_based] == ""
                        or row[col_zero_based] is None
                    ):
                        missing_fields.append(
                            {
                                "row": row_idx + 1,
                                "col": col_idx,
                                "field": f"Column {col_idx}",
                            }
                        )

            # Record results (this validator only flags, doesn't fix)
            if missing_fields:
                result.add_issue(len(missing_fields))
                result.details["missing_fields"] = missing_fields
                result.set_automated_log(
                    f"Missing required fields: {len(missing_fields)} entries"
                )

                # Note: Fix mode does nothing for this validator since we cannot
                # automatically determine what values should be filled in
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
