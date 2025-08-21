"""
Tab Name Consistency Validator.

This validator checks that tab names referenced in verification_field_ranges
exist (with exact casing) in BOTH input and output Google Sheets.

Goal:
Ensure that all tabs referenced in verification ranges are present and
correctly named in both input and output spreadsheets.

Why:
If verification ranges reference tabs that don't exist or have incorrect
casing, the validation process will fail. This validator catches such
flags early.
"""

from __future__ import annotations
import re
from typing import Any, Dict, List, Union
from pathlib import Path
import pandas as pd

from urarovite.validators.base import BaseValidator, ValidationResult
from urarovite.core.exceptions import ValidationError
from urarovite.utils.sheets import fetch_sheet_tabs
from urarovite.core.spreadsheet import SpreadsheetInterface


class TabNameConsistencyValidator(BaseValidator):
    """Validator that checks tab name consistency between input and output spreadsheets."""

    def __init__(self) -> None:
        super().__init__(
            validator_id="tab_name_consistency",
            name="Tab Name Consistency",
            description="Checks that tab names referenced in verification ranges exist in both input and output sheets",
        )

    def _parse_referenced_tabs(self, ranges_str: str) -> List[str]:
        """Parse tab names from verification ranges string."""
        if not ranges_str or pd.isna(ranges_str):
            return []

        # Pattern to match 'TabName'!A1:B2 or "TabName"!A1:B2
        pattern = r"['\"]([^'\"]+)['\"]!"
        matches = re.findall(pattern, str(ranges_str))
        return list(set(matches))  # Remove duplicates

    def _extract_sheet_id(self, url: str) -> str:
        """Extract sheet ID from Google Sheets URL."""
        if not url or pd.isna(url):
            return ""

        # Pattern to match Google Sheets URL and extract ID
        pattern = r"/spreadsheets/d/([a-zA-Z0-9-_]+)"
        match = re.search(pattern, str(url))
        return match.group(1) if match else ""

    def _create_case_map(self, tabs: List[str]) -> Dict[str, str]:
        """Create a mapping from lowercase tab names to actual tab names."""
        cmap = {}
        for tab in tabs:
            lc = tab.lower()
            if lc not in cmap:
                cmap[lc] = tab
        return cmap

    def validate(
        self,
        spreadsheet_source: Union[str, Path, SpreadsheetInterface],
        mode: str,
        auth_credentials: Dict[str, Any] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Execute tab name consistency validation.

        Args:
            spreadsheet_source: Either a Google Sheets URL, Excel file path,
                or SpreadsheetInterface (not used for this validator - uses URLs from row data)
            mode: Either "fix" (not applicable) or "flag" (report only)
            auth_credentials: Authentication credentials (required for Google Sheets)
            **kwargs: Must contain 'row' with pandas Series or dict containing the data

        Returns:
            Dict with validation results
        """
        # For now, we'll use a simple approach and delegate to the old interface
        # TODO: Fully update this validator to use the abstraction layer
        from urarovite.auth.google_sheets import (
            create_sheets_service_from_encoded_creds,
        )

        result = ValidationResult()

        try:
            if auth_credentials:
                auth_secret = auth_credentials.get("auth_secret")
                sheets_service = (
                    create_sheets_service_from_encoded_creds(auth_secret)
                    if auth_secret
                    else None
                )
            else:
                sheets_service = None
        except Exception:
            sheets_service = None

        try:
            # Extract parameters
            row = kwargs.get("row")
            if row is None:
                # Return empty result if no row data provided
                result.details["missing_in_input"] = []
                result.details["missing_in_output"] = []
                result.details["case_mismatches_input"] = []
                result.details["case_mismatches_output"] = []
                result.set_automated_log("No flags found")
                return result.to_dict()

            input_col = kwargs.get("input_col", "input_sheet_url")
            output_col = kwargs.get("output_col", "example_output_sheet_url")
            ranges_col = kwargs.get("ranges_col", "verification_field_ranges")

            # Extract data from row
            input_url = row.get(input_col, None)
            output_url = row.get(output_col, None)
            ranges_str = row.get(ranges_col, "")

            # Parse referenced tabs and extract sheet IDs
            referenced_tabs = self._parse_referenced_tabs(ranges_str)
            input_id = self._extract_sheet_id(input_url)
            output_id = self._extract_sheet_id(output_url)

            # Fetch sheet metadata
            input_meta = fetch_sheet_tabs(sheets_service, input_id)
            output_meta = fetch_sheet_tabs(sheets_service, output_id)

            # Check for basic errors
            errors: List[str] = []
            if not referenced_tabs:
                errors.append("no_verification_ranges")
            if not input_meta["accessible"]:
                errors.append("input_inaccessible")
            if not output_meta["accessible"]:
                errors.append("output_inaccessible")

            # Initialize result lists

            # Perform consistency checks if both sheets are accessible
            if (
                input_meta["accessible"]
                and output_meta["accessible"]
                and referenced_tabs
            ):
                input_tabs = input_meta["tabs"]
                output_tabs = output_meta["tabs"]

                # Create case-insensitive lookups
                input_lower = set(t.lower() for t in input_tabs)
                output_lower = set(t.lower() for t in output_tabs)
                input_case_map = self._create_case_map(input_tabs)
                output_case_map = self._create_case_map(output_tabs)

                # Create exact case lookups
                input_set = set(input_tabs)
                output_set = set(output_tabs)

                # Check each referenced tab
                for tab in referenced_tabs:
                    # Check input sheet
                    if tab not in input_set:
                        if tab.lower() in input_lower:
                            actual = input_case_map[tab.lower()]
                            result.add_detailed_issue(
                                sheet_name=input_url,
                                cell=tab,
                                message=f"Tab name case mismatch in input sheet. Expected '{tab}', found '{actual}'.",
                                value=tab,
                            )
                        else:
                            result.add_detailed_issue(
                                sheet_name=input_url,
                                cell=tab,
                                message=f"Tab '{tab}' is missing from the input sheet.",
                                value=tab,
                            )

                    # Check output sheet
                    if tab not in output_set:
                        if tab.lower() in output_lower:
                            actual = output_case_map[tab.lower()]
                            result.add_detailed_issue(
                                sheet_name=output_url,
                                cell=tab,
                                message=f"Tab name case mismatch in output sheet. Expected '{tab}', found '{actual}'.",
                                value=tab,
                            )
                        else:
                            result.add_detailed_issue(
                                sheet_name=output_url,
                                cell=tab,
                                message=f"Tab '{tab}' is missing from the output sheet.",
                                value=tab,
                            )

            # Create ValidationResult and populate details
            result.details["errors"] = errors
            result.details["sheets"] = {
                "input": input_meta,
                "output": output_meta,
            }

            # Generate flags and automated log
            if result.flags_found > 0:
                result.set_automated_log(
                    f"Found {result.flags_found} tab name consistency flags."
                )
            elif errors:
                result.set_automated_log(
                    f"Validation failed with errors: {'; '.join(errors)}"
                )
            else:
                result.set_automated_log("No tab name consistency flags found.")

        except Exception as e:
            result.add_error(f"Unexpected error: {str(e)}")
            result.set_automated_log("Validation failed")

        return result.to_dict()


# Convenience function for backward compatibility
def run(
    row: Union[Dict[str, Any], "pd.Series"],
    input_col: str = "input_sheet_url",
    output_col: str = "example_output_sheet_url",
    ranges_col: str = "verification_field_ranges",
) -> Dict[str, Any]:
    """
    Execute tab name consistency check.
    This function provides backward compatibility with the original checker3 interface.
    """
    # Import here to avoid circular imports
    from urarovite.auth.google_sheets import create_sheets_service_from_encoded_creds

    validator = TabNameConsistencyValidator()

    try:
        # For backward compatibility, we still need to use the old interface
        # since this validator hasn't been fully updated to the new abstraction layer
        # This is a temporary solution until all validators are migrated

        # Create a minimal sheets service for the old interface
        # In practice, this validator should be updated to use the new interface
        service = (
            None  # This validator doesn't actually use the sheets_service parameter
        )

        return validator.validate(
            sheets_service=service,
            sheet_id="",  # Not used by this validator
            mode="flag",
            row=row,
            input_col=input_col,
            output_col=output_col,
            ranges_col=ranges_col,
        )
    except Exception as e:
        # Return error in ValidationResult format
        result = ValidationResult()
        result.add_error(f"validation_error: {str(e)}")
        result.details["sheets"] = {
            "input": {"id": None, "accessible": False, "tabs": [], "error": str(e)},
            "output": {"id": None, "accessible": False, "tabs": [], "error": str(e)},
        }
        result.set_automated_log("Validation failed")
        return result.to_dict()
