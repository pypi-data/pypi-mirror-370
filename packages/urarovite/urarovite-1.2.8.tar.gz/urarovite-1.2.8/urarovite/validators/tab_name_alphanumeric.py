"""
Tab Name Alphanumeric Validator.

This validator ensures that all tab names contain only alphanumeric characters
(letters and numbers) and spaces. Non-alphanumeric characters (except spaces)
are omitted, and consecutive spaces are collapsed to single spaces.
Underscores are converted to spaces for better readability.

Goal:
Sanitize tab names to be alphanumeric with spaces for maximum compatibility
across different systems while maintaining readability.

Why:
Tab names with special characters can cause issues in various contexts:
- API integrations that expect clean identifiers
- Export/import operations
- Formula references
- Database operations
- Cross-platform compatibility
"""

from __future__ import annotations
from typing import Any, Dict, List, Union
from pathlib import Path

from urarovite.validators.base import BaseValidator, ValidationResult
from urarovite.core.spreadsheet import SpreadsheetInterface
from urarovite.utils.tab_name_sanitizer import (
    sanitize_tab_name,
    detect_non_alphanumeric_tabs,
    ensure_unique_names
)


class TabNameAlphanumericValidator(BaseValidator):
    """Validator that fixes tab names to be alphanumeric with spaces only."""

    def __init__(self) -> None:
        super().__init__(
            validator_id="tab_name_alphanumeric",
            name="Tab Name Alphanumeric",
            description=(
                "Ensures tab names contain only letters, numbers, and spaces; "
                "converts underscores to spaces for better readability"
            ),
        )

    def _detect_non_alphanumeric_tabs(self, tab_names: List[str]) -> Dict[str, str]:
        """Detect tab names that need alphanumeric with spaces sanitization.

        Args:
            tab_names: List of tab names to check

        Returns:
            Dict mapping original tab names to their sanitized versions
            (only includes tabs that actually need changes)
        """
        return detect_non_alphanumeric_tabs(tab_names)

    def _ensure_unique_names(
        self, rename_mapping: Dict[str, str], all_tab_names: List[str]
    ) -> Dict[str, str]:
        """Ensure all sanitized names are unique by adding numeric suffixes if
        needed.

        Args:
            rename_mapping: Dict of original names to sanitized names
            all_tab_names: All existing tab names

        Returns:
            Updated rename mapping with unique names
        """
        return ensure_unique_names(rename_mapping, all_tab_names)

    def _validate_with_explicit_write_access(
        self,
        spreadsheet_source: Union[str, Path, SpreadsheetInterface],
        mode: str,
        auth_credentials: Dict[str, Any] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Special validation method that ensures write access for tab renaming.


        This bypasses the BaseValidator's managed spreadsheet to ensure we get

        write access for tab renaming operations.
        """
        result = ValidationResult()

        try:
            # If we already have a SpreadsheetInterface, use it directly
            if isinstance(spreadsheet_source, SpreadsheetInterface):
                spreadsheet = spreadsheet_source

                # Force set read_only to False if possible
                if hasattr(spreadsheet, "read_only"):
                    spreadsheet.read_only = False

            else:
                # Create spreadsheet with explicit write access
                from urarovite.core.spreadsheet import SpreadsheetFactory

                spreadsheet = SpreadsheetFactory.create_spreadsheet(
                    spreadsheet_source, auth_credentials, read_only=False
                )

            # Execute the core validation logic

            self._execute_tab_validation_logic(
                spreadsheet, result, mode, spreadsheet_source, auth_credentials
            )

        except Exception as e:
            result.add_error(f"Validation failed: {str(e)}")

            self.logger.exception("Error in explicit write access validation")

        return result.to_dict()

    def _execute_tab_validation_logic(
        self,
        spreadsheet: SpreadsheetInterface,
        result: ValidationResult,
        mode: str,
        spreadsheet_source: Union[str, Path, SpreadsheetInterface],
        auth_credentials: Dict[str, Any],
    ) -> None:
        """Execute the core tab validation logic."""
        # Check if spreadsheet is still read-only
        if hasattr(spreadsheet, "read_only") and spreadsheet.read_only:
            result.add_error("Cannot rename tabs: spreadsheet is in read-only mode")
            result.set_automated_log("Validation failed due to read-only access")
            return

        # Get tab names using generic utility
        try:
            from urarovite.utils.generic_spreadsheet import (
                get_spreadsheet_tabs,
            )

            tabs_result = get_spreadsheet_tabs(spreadsheet_source, auth_credentials)

            if not tabs_result["accessible"]:
                error_msg = f"Unable to access spreadsheet: {tabs_result['error']}"
                result.add_error(error_msg)
                result.set_automated_log("Sheet access failed")
                return

            tab_names = tabs_result["tabs"]
            if not tab_names:
                result.set_automated_log("No tabs found in spreadsheet")
                return

        except Exception as e:
            result.add_error(f"Failed to get sheet names: {str(e)}")
            result.set_automated_log("Sheet access failed")
            return

        # Detect tabs that need alphanumeric with spaces sanitization
        rename_mapping = self._detect_non_alphanumeric_tabs(tab_names)

        if not rename_mapping:
            result.set_automated_log(
                "All tab names are already alphanumeric with spaces only"
            )
            return

        # Ensure unique names after sanitization
        unique_rename_mapping = self._ensure_unique_names(rename_mapping, tab_names)

        # Log flags and fixes for each tab that needs changes
        for original_name, sanitized_name in unique_rename_mapping.items():
            message = (
                f"Tab name contains invalid characters (only letters, "
                f"numbers, and spaces allowed): '{original_name}'"
            )

            if mode == "fix":
                result.add_detailed_fix(
                    sheet_name=original_name,
                    cell="N/A",
                    message=(
                        f"Sanitized tab name to contain only letters, "
                        f"numbers, and spaces. {message}"
                    ),
                    old_value=original_name,
                    new_value=sanitized_name,
                )
            else:  # Flag mode
                result.add_detailed_issue(
                    sheet_name=original_name,
                    cell="N/A",
                    message=message,
                    value=original_name,
                )

        if mode == "fix":
            # Apply the renames using the spreadsheet interface directly
            apply_errors = []

            for original_name, sanitized_name in unique_rename_mapping.items():
                try:
                    # Use the spreadsheet object directly (it should be in
                    # write mode)
                    spreadsheet.update_sheet_properties(
                        sheet_name=original_name, new_name=sanitized_name
                    )
                except Exception as e:
                    apply_errors.append(f"Failed to rename '{original_name}': {str(e)}")

            if apply_errors:
                for error in apply_errors:
                    result.add_error(error)
                result.set_automated_log(
                    f"Found {len(unique_rename_mapping)} tabs needing "
                    f"sanitization fixes, but encountered errors during "
                    f"rename."
                )
            else:
                # Save the changes to persist tab renames
                try:
                    spreadsheet.save()
                except Exception as e:
                    result.add_error(f"Failed to save changes: {str(e)}")

                result.set_automated_log(
                    f"Fixed {result.fixes_applied} tab names to contain only "
                    f"letters, numbers, and spaces."
                )
        else:
            # Flag mode - just report
            result.set_automated_log(
                f"Found {result.flags_found} tab names with invalid characters."
            )

    def validate(
        self,
        spreadsheet_source: Union[str, Path, SpreadsheetInterface],
        mode: str,
        auth_credentials: Dict[str, Any] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Execute tab name alphanumeric validation.

        Args:
            spreadsheet_source: Either a Google Sheets URL, Excel file path,
                or SpreadsheetInterface
            mode: Either "fix" (auto-correct) or "flag" (report only)
            auth_credentials: Authentication credentials (required for Google
                Sheets)
            **kwargs: Additional validator-specific parameters

        Returns:
            Dict with validation results including tab name changes
        """

        # For fix mode with tab renaming, we need to ensure write access
        # Override the BaseValidator to manually manage write access
        if mode == "fix":
            return self._validate_with_explicit_write_access(
                spreadsheet_source, mode, auth_credentials, **kwargs
            )

        def validation_logic(
            spreadsheet: SpreadsheetInterface, result: ValidationResult, **kwargs
        ) -> None:
            # Get tab names using generic utility that works with both Google
            # Sheets and Excel
            try:
                from urarovite.utils.generic_spreadsheet import (
                    get_spreadsheet_tabs,
                )

                tabs_result = get_spreadsheet_tabs(spreadsheet_source, auth_credentials)

                if not tabs_result["accessible"]:
                    error_msg = f"Unable to access spreadsheet: {tabs_result['error']}"
                    result.add_error(error_msg)
                    result.set_automated_log("Sheet access failed")
                    return

                tab_names = tabs_result["tabs"]
                if not tab_names:
                    result.set_automated_log("No tabs found in spreadsheet")
                    return

            except Exception as e:
                result.add_error(f"Failed to get sheet names: {str(e)}")
                result.set_automated_log("Sheet access failed")
                return

            # Detect tabs that need alphanumeric with spaces sanitization
            rename_mapping = self._detect_non_alphanumeric_tabs(tab_names)

            if not rename_mapping:
                # All tab names are already alphanumeric with spaces only
                result.set_automated_log(
                    "All tab names are already alphanumeric with spaces only"
                )
                return

            # Ensure unique names after sanitization
            unique_rename_mapping = self._ensure_unique_names(rename_mapping, tab_names)

            # Log flags and fixes for each tab that needs changes
            for original_name, sanitized_name in unique_rename_mapping.items():
                message = (
                    f"Tab name contains invalid characters (only letters, "
                    f"numbers, and spaces allowed): '{original_name}'"
                )

                if mode == "fix":
                    result.add_detailed_fix(
                        sheet_name=original_name,
                        cell="N/A",
                        message=(
                            f"Sanitized tab name to contain only letters, "
                            f"numbers, and spaces. {message}"
                        ),
                        old_value=original_name,
                        new_value=sanitized_name,
                    )
                else:  # Flag mode
                    result.add_detailed_issue(
                        sheet_name=original_name,
                        cell="N/A",
                        message=message,
                        value=original_name,
                    )

            if mode == "fix":
                # Apply the renames using the spreadsheet interface
                # directly
                apply_errors = []

                for original_name, sanitized_name in unique_rename_mapping.items():
                    try:
                        # Use the spreadsheet object directly (it's in
                        # write mode)
                        spreadsheet.update_sheet_properties(
                            sheet_name=original_name, new_name=sanitized_name
                        )
                    except Exception as e:
                        apply_errors.append(
                            f"Failed to rename '{original_name}': {str(e)}"
                        )

                if apply_errors:
                    for error in apply_errors:
                        result.add_error(error)
                    result.set_automated_log(
                        f"Found {len(unique_rename_mapping)} tabs needing "
                        f"sanitization fixes, but encountered errors during "
                        f"rename."
                    )
                else:
                    # Save the changes to persist tab renames
                    try:
                        spreadsheet.save()
                    except Exception as e:
                        result.add_error(f"Failed to save changes: {str(e)}")

                    result.set_automated_log(
                        f"Fixed {result.fixes_applied} tab names to contain "
                        f"only "
                        f"letters, numbers, and spaces."
                    )
            else:
                # Flag mode - just report
                result.set_automated_log(
                    f"Found {result.flags_found} tab names with invalid characters."
                )

        return self._execute_validation(
            validation_logic, spreadsheet_source, auth_credentials, **kwargs
        )


# Convenience function for standalone usage
def sanitize_tab_names_to_alphanumeric(tab_names: List[str]) -> Dict[str, Any]:
    """
    Standalone function to analyze and suggest sanitization for tab names.
    Ensures tab names contain only letters, numbers, and spaces.

    Args:
        tab_names: List of tab names to analyze

    Returns:
        Dict with sanitization analysis and suggested rename mapping
    """
    validator = TabNameAlphanumericValidator()

    rename_mapping = validator._detect_non_alphanumeric_tabs(tab_names)

    if not rename_mapping:
        return {
            "needs_sanitization": False,
            "suggested_mapping": {},
            "tabs_affected": 0,
        }

    unique_mapping = validator._ensure_unique_names(rename_mapping, tab_names)

    return {
        "needs_sanitization": True,
        "suggested_mapping": unique_mapping,
        "tabs_affected": len(unique_mapping),
        "preview": [
            {"original": orig, "sanitized": san} for orig, san in unique_mapping.items()
        ],
    }
