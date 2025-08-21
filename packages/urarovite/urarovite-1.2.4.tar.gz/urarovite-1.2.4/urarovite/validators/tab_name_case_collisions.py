"""
Tab Name Case Collisions Validator.

This validator detects tab names that differ only by case (which are
Excel-insensitive collisions) and optionally fixes them by appending
numeric suffixes like (2), (3), etc.

Goal:
Ensure tab names are Excel-safe by eliminating case-only collisions
that could cause flags when working with Excel files.

Why:
Excel treats tab names case-insensitively, so "Sheet1" and "sheet1"
would be considered the same tab name. This can cause flags when
exporting or working with Excel formats.
"""

from __future__ import annotations
from typing import Any, Dict, List, Set, Union
from collections import defaultdict
from pathlib import Path

from urarovite.validators.base import BaseValidator, ValidationResult
from urarovite.core.spreadsheet import SpreadsheetInterface
from urarovite.utils.sheets import fetch_sheet_tabs


class TabNameCaseCollisionsValidator(BaseValidator):
    """Validator that detects and fixes case-only collisions in tab names."""

    def __init__(self) -> None:
        super().__init__(
            validator_id="tab_name_case_collisions",
            name="Tab Name Case Collisions",
            description=(
                "Detects tabs differing only by case (Excel-insensitive); "
                "append (2), (3) suffix; emit mapping"
            ),
        )

    def _detect_case_collisions(self, tab_names: List[str]) -> Dict[str, List[str]]:
        """Detect groups of tab names that differ only by case.

        Args:
            tab_names: List of tab names to check

        Returns:
            Dict mapping lowercase names to lists of actual tab names that match
        """
        case_groups = defaultdict(list)

        for tab_name in tab_names:
            lowercase_key = tab_name.lower()
            case_groups[lowercase_key].append(tab_name)

        # Only return groups with collisions (more than one tab)
        return {key: names for key, names in case_groups.items() if len(names) > 1}

    def _generate_safe_name(self, base_name: str, existing_names: Set[str]) -> str:
        """Generate a safe tab name by appending a numeric suffix.

        Args:
            base_name: The original tab name
            existing_names: Set of already used names (case-insensitive)

        Returns:
            A safe name that doesn't collide with existing names
        """
        if base_name.lower() not in existing_names:
            return base_name

        # Try appending (2), (3), etc.
        counter = 2
        while True:
            candidate = f"{base_name} ({counter})"
            if candidate.lower() not in existing_names:
                return candidate
            counter += 1

    def _create_rename_mapping(
        self, collisions: Dict[str, List[str]]
    ) -> Dict[str, str]:
        """Create a mapping of old names to new names for fixing collisions.

        Args:
            collisions: Dict of collision groups

        Returns:
            Dict mapping original tab names to new safe names
        """
        rename_mapping = {}
        used_names = set()

        # First, collect all existing lowercase names to avoid new collisions
        for names_list in collisions.values():
            for name in names_list:
                used_names.add(name.lower())

        for collision_group in collisions.values():
            # Keep the first name unchanged, rename the rest
            first_name = collision_group[0]
            rename_mapping[first_name] = first_name

            for duplicate_name in collision_group[1:]:
                safe_name = self._generate_safe_name(duplicate_name, used_names)
                rename_mapping[duplicate_name] = safe_name
                used_names.add(safe_name.lower())

        return rename_mapping

    def _apply_tab_renames(
        self, sheets_service: Any, spreadsheet_id: str, rename_mapping: Dict[str, str]
    ) -> List[str]:
        """Apply tab name changes to the spreadsheet.

        Args:
            sheets_service: Google Sheets API service instance
            spreadsheet_id: ID of the spreadsheet
            rename_mapping: Dict mapping old names to new names

        Returns:
            List of error messages if any operations failed
        """
        errors = []

        try:
            # Get sheet metadata to find sheet IDs
            sheet_metadata = (
                sheets_service.spreadsheets()
                .get(spreadsheetId=spreadsheet_id)
                .execute()
            )

            # Create mapping from sheet names to sheet IDs
            name_to_id = {}
            for sheet in sheet_metadata.get("sheets", []):
                sheet_props = sheet.get("properties", {})
                name_to_id[sheet_props.get("title", "")] = sheet_props.get("sheetId")

            # Build batch update requests
            requests = []
            for old_name, new_name in rename_mapping.items():
                if old_name != new_name:  # Only rename if actually different
                    sheet_id = name_to_id.get(old_name)
                    if sheet_id is not None:
                        requests.append(
                            {
                                "updateSheetProperties": {
                                    "properties": {
                                        "sheetId": sheet_id,
                                        "title": new_name,
                                    },
                                    "fields": "title",
                                }
                            }
                        )
                    else:
                        errors.append(f"Could not find sheet ID for tab '{old_name}'")

            # Execute batch update if we have requests
            if requests:
                body = {"requests": requests}
                sheets_service.spreadsheets().batchUpdate(
                    spreadsheetId=spreadsheet_id, body=body
                ).execute()

        except Exception as e:
            errors.append(f"Failed to apply tab renames: {str(e)}")

        return errors

    def validate(
        self,
        spreadsheet_source: Union[str, Path, SpreadsheetInterface],
        mode: str,
        auth_credentials: Dict[str, Any] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Execute tab name case collision validation.

        Args:
            spreadsheet_source: Either a Google Sheets URL, Excel file path,
                or SpreadsheetInterface
            mode: Either "fix" (auto-correct) or "flag" (report only)
            auth_credentials: Authentication credentials (required for Google Sheets)
            **kwargs: Additional validator-specific parameters

        Returns:
            Dict with validation results including collision details and mapping
        """

        def validation_logic(
            spreadsheet: SpreadsheetInterface, result: ValidationResult, **kwargs
        ) -> None:
            # Use generic utility that works with both Google Sheets and Excel
            try:
                from urarovite.utils.generic_spreadsheet import get_spreadsheet_tabs

                tabs_result = get_spreadsheet_tabs(spreadsheet_source, auth_credentials)

                if not tabs_result["accessible"]:
                    error_msg = f"Unable to access spreadsheet: {tabs_result['error']}"
                    result.add_error(error_msg)
                    result.set_automated_log("Sheet access failed")
                    return

                tab_names = tabs_result["tabs"]
            except Exception as e:
                result.add_error(f"Failed to get sheet names: {str(e)}")
                result.set_automated_log("Sheet access failed")
                return

            # Detect case collisions
            collisions = self._detect_case_collisions(tab_names)

            if not collisions:
                # No collisions found
                result.set_automated_log("No case collisions found")
                return

            rename_mapping = self._create_rename_mapping(collisions)

            # Log flags and fixes
            for collision_group in collisions.values():
                for i, tab_name in enumerate(collision_group):
                    new_name = rename_mapping.get(tab_name, tab_name)
                    message = (
                        f"Tab name case collision with: {', '.join(collision_group)}"
                    )

                    if i == 0:  # First one is the original, but still an issue
                        result.add_detailed_issue(
                            sheet_name=tab_name,
                            cell="N/A",
                            message=message,
                            value=tab_name,
                        )
                    elif mode == "fix":
                        result.add_detailed_fix(
                            sheet_name=tab_name,
                            cell="N/A",
                            message=f"Resolved case collision. {message}",
                            old_value=tab_name,
                            new_value=new_name,
                        )
                    else:  # Flag mode for subsequent tabs
                        result.add_detailed_issue(
                            sheet_name=tab_name,
                            cell="N/A",
                            message=message,
                            value=tab_name,
                        )

            if mode == "fix":
                # Apply the renames using generic utility
                from urarovite.utils.generic_spreadsheet import rename_spreadsheet_sheet

                apply_errors = []

                for old_name, new_name in rename_mapping.items():
                    if old_name == new_name:
                        continue  # No rename needed

                    rename_result = rename_spreadsheet_sheet(
                        spreadsheet_source, old_name, new_name, auth_credentials
                    )
                    if not rename_result["success"]:
                        apply_errors.append(rename_result["error"])

                if apply_errors:
                    for error in apply_errors:
                        result.add_error(error)
                    result.set_automated_log(
                        f"Found {len(collisions)} case collision groups, but encountered errors during fix."
                    )
                else:
                    result.set_automated_log(
                        f"Fixed {result.fixes_applied} tab name case collisions."
                    )
            else:
                # Flag mode - just report
                result.set_automated_log(
                    f"Found {result.flags_found} tabs with case collisions."
                )

        return self._execute_validation(
            validation_logic, spreadsheet_source, auth_credentials, **kwargs
        )


# Convenience function for standalone usage
def detect_tab_case_collisions(tab_names: List[str]) -> Dict[str, Any]:
    """
    Standalone function to detect case collisions in a list of tab names.

    Args:
        tab_names: List of tab names to check

    Returns:
        Dict with collision information and suggested rename mapping
    """
    validator = TabNameCaseCollisionsValidator()

    collisions = validator._detect_case_collisions(tab_names)

    if not collisions:
        return {
            "has_collisions": False,
            "collisions": {},
            "suggested_mapping": {},
            "tabs_affected": 0,
        }

    rename_mapping = validator._create_rename_mapping(collisions)
    total_affected = sum(len(names) for names in collisions.values())

    return {
        "has_collisions": True,
        "collisions": collisions,
        "suggested_mapping": rename_mapping,
        "tabs_affected": total_affected,
    }
