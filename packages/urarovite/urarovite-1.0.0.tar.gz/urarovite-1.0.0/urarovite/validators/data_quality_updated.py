"""Updated data quality validators using the spreadsheet abstraction layer.

This module demonstrates how to update validators to work with both
Google Sheets and Excel files using the new abstraction layer.
"""

from typing import Any, Dict, List, Union
from pathlib import Path

from urarovite.validators.base import BaseValidator, ValidationResult
from urarovite.core.exceptions import ValidationError
from urarovite.core.spreadsheet import SpreadsheetInterface


class EmptyCellsValidatorUpdated(BaseValidator):
    """Updated validator for identifying and fixing empty cells."""

    def __init__(self) -> None:
        super().__init__(
            validator_id="empty_cells",
            name="Fix Empty Cells",
            description="Identifies and optionally fills empty cells with default values",
        )

    def validate(
        self,
        spreadsheet_source: Union[str, Path, SpreadsheetInterface],
        mode: str,
        auth_credentials: Dict[str, Any] = None,
        fill_value: str = "",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Check for and optionally fix empty cells.

        Args:
            spreadsheet_source: Either a Google Sheets URL, Excel file path, or SpreadsheetInterface
            mode: Either "fix" (fill empty cells) or "flag" (report only)
            auth_credentials: Authentication credentials (required for Google Sheets)
            fill_value: Value to use when filling empty cells (default: "")

        Returns:
            Dict with validation results
        """
        result = ValidationResult()
        spreadsheet = None

        try:
            # Get spreadsheet interface
            spreadsheet = self._get_spreadsheet(spreadsheet_source, auth_credentials, read_only=mode != 'fix')
            
            # Get all sheet data and sheet name
            data, sheet_name = self._get_all_sheet_data(spreadsheet)

            if not data:
                result.details["message"] = "No data found to validate"
                result.set_automated_log("No data found to validate")
                return result.to_dict()
            
            empty_cells = []
            fixed_data = []

            # Check each row for empty cells
            for row_idx, row in enumerate(data):
                fixed_row = []
                for col_idx, cell in enumerate(row):
                    if cell == "" or cell is None:
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
                    result.set_automated_log(f"Fixed empty cells at positions: {empty_cells}")
                else:
                    result.add_issue(len(empty_cells))
                    result.details["empty_cells"] = empty_cells
                    result.set_automated_log(f"Empty cells found at positions: {empty_cells}")
            else:
                result.set_automated_log("No issues found")

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


class TabNameValidatorUpdated(BaseValidator):
    """Updated validator for checking and fixing tab names."""

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
            spreadsheet_source: Either a Google Sheets URL, Excel file path, or SpreadsheetInterface
            mode: Either "fix" (fix tab names) or "flag" (report only)
            auth_credentials: Authentication credentials (required for Google Sheets)
            replacement_char: Character to replace illegal characters with (default: "_")

        Returns:
            Dict with validation results including mapping of changes
        """
        result = ValidationResult()
        spreadsheet = None

        try:
            # Get spreadsheet interface
            spreadsheet = self._get_spreadsheet(spreadsheet_source, auth_credentials, read_only=mode != 'fix')
            
            # Get spreadsheet metadata
            metadata = spreadsheet.get_metadata()
            sheet_names = metadata.sheet_names

            if not sheet_names:
                result.add_error("No sheets found in spreadsheet")
                result.set_automated_log("No issues found")
                return result.to_dict()

            # Import constants from original validator
            from urarovite.validators.data_quality import (
                ILLEGAL_CHARS, 
                EXCEL_MAX_TAB_NAME_LENGTH,
                COLLISION_SUFFIX_LENGTH,
                MAX_BASE_NAME_LENGTH
            )

            # Collect all existing tab names for collision detection
            all_tab_names = set(sheet_names)

            tab_issues = []
            name_mapping = {}
            used_names = set(all_tab_names)  # Track all names to avoid collisions

            # Check each tab for illegal characters and length violations
            for sheet_name in sheet_names:
                # Check for illegal characters: \ / ? * [ ]
                has_illegal_chars = any(char in sheet_name for char in ILLEGAL_CHARS)
                
                # Check for Excel length violation (>31 characters)
                exceeds_excel_limit = len(sheet_name) > EXCEL_MAX_TAB_NAME_LENGTH

                if has_illegal_chars or exceeds_excel_limit:
                    # Start with the original name
                    fixed_name = sheet_name
                    
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
                    name_mapping[sheet_name] = final_name

                    # Record detected issues
                    detected_chars = [
                        char for char in ILLEGAL_CHARS if char in sheet_name
                    ] if has_illegal_chars else []

                    issue_types = []
                    if has_illegal_chars:
                        issue_types.append("illegal_characters")
                    if exceeds_excel_limit:
                        issue_types.append("excel_length_limit")

                    tab_issues.append(
                        {
                            "original_name": sheet_name,
                            "fixed_name": final_name,
                            "original_length": len(sheet_name),
                            "fixed_length": len(final_name),
                            "illegal_chars": detected_chars,
                            "issue_types": issue_types,
                        }
                    )

            # Record results
            if tab_issues:
                if mode == "fix":
                    # Update tab names
                    for issue in tab_issues:
                        spreadsheet.update_sheet_properties(
                            sheet_name=issue["original_name"],
                            new_name=issue["fixed_name"]
                        )
                    
                    # Save changes (important for Excel files)
                    spreadsheet.save()
                    
                    result.add_fix(len(tab_issues))
                    result.details["fixed_tabs"] = tab_issues
                    result.details["name_mapping"] = name_mapping
                    result.set_automated_log(f"Fixed tab names: {tab_issues}")
                else:
                    result.add_issue(len(tab_issues))
                    result.details["tab_issues"] = tab_issues
                    result.details["proposed_mapping"] = name_mapping
                    result.set_automated_log(f"Tab name issues found: {tab_issues}")
            else:
                result.set_automated_log("No issues found")

        except ValidationError:
            raise
        except Exception as e:
            result.add_error(f"Unexpected error: {str(e)}")
            result.set_automated_log("No issues found")
        finally:
            # Clean up resources
            if spreadsheet:
                try:
                    spreadsheet.close()
                except Exception:
                    pass  # Ignore cleanup errors

        return result.to_dict()

    def _clean_tab_name(self, tab_name: str, replacement_char: str) -> str:
        """Clean a tab name by replacing illegal characters."""
        # Import from original validator to reuse logic
        from urarovite.validators.data_quality import TabNameValidator
        validator = TabNameValidator()
        return validator._clean_tab_name(tab_name, replacement_char)

    def _resolve_name_collision(self, proposed_name: str, used_names: set) -> str:
        """Resolve name collisions by appending numbers."""
        # Import from original validator to reuse logic
        from urarovite.validators.data_quality import TabNameValidator
        validator = TabNameValidator()
        return validator._resolve_name_collision(proposed_name, used_names)

    def _truncate_for_excel(self, tab_name: str, used_names: set) -> str:
        """Truncate tab name to Excel's 31-character limit."""
        # Import from original validator to reuse logic
        from urarovite.validators.data_quality import TabNameValidator
        validator = TabNameValidator()
        return validator._truncate_for_excel(tab_name, used_names)
