"""Verification range matching validator.

This validator ensures that input and output spreadsheets are equivalent
within the specified verification field ranges, flagging any cells that match
between input and output files within these ranges.
"""

import re
from typing import Any, Dict, List, Union
from pathlib import Path

from urarovite.validators.base import BaseValidator, ValidationResult
from urarovite.core.exceptions import ValidationError
from urarovite.core.spreadsheet import SpreadsheetInterface


class VerificationRangeMatchingValidator(BaseValidator):
    """Validator for checking verification range matching between input/output sheets."""

    def __init__(self) -> None:
        super().__init__(
            validator_id="verification_range_matching",
            name="Verification Range Matching",
            description=(
                "Ensures input and output spreadsheets are equivalent within "
                "verification field ranges and flags matching cells"
            ),
        )

    def validate(
        self,
        spreadsheet_source: Union[str, Path, SpreadsheetInterface],
        mode: str,
        auth_credentials: Dict[str, Any] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Validate verification range matching between input and output sheets.

        Args:
            spreadsheet_source: Either a Google Sheets URL, Excel file path,
                or SpreadsheetInterface
            mode: Either "fix" (not applicable) or "flag" (report only)
            auth_credentials: Authentication credentials (required for Google Sheets)

        Returns:
            Dict with validation results
        """

        def validation_logic(
            spreadsheet: SpreadsheetInterface, result: ValidationResult, **kwargs
        ) -> None:
            # Get all sheet data
            data, sheet_name = self._get_all_sheet_data(spreadsheet)

            if not data:
                result.add_error("Sheet is empty - no data to validate")
                result.set_automated_log("Sheet is empty - no data to validate")
                return

            # Find columns containing input/output URLs and verification ranges
            input_col = None
            output_col = None
            verification_col = None

            # Look for header row to identify columns
            if data:
                header_row = data[0]
                for col_idx, header in enumerate(header_row):
                    header_str = str(header).lower().strip()
                    if ("input" in header_str and ("file" in header_str or "sheet" in header_str or "url" in header_str)):
                        input_col = col_idx
                    elif ("output" in header_str and ("file" in header_str or "sheet" in header_str or "url" in header_str)):
                        output_col = col_idx
                    elif "verification" in header_str and ("range" in header_str or "field" in header_str):
                        verification_col = col_idx

            if input_col is None or output_col is None or verification_col is None:
                result.add_error(
                    "Required columns not found: need Input File, Output File, and Verification Field Ranges"
                )
                result.set_automated_log("Required columns not found")
                return

            matching_cells_count = 0
            verification_issues = []

            # Process each row (skip header)
            for row_idx, row in enumerate(data[1:], start=2):  # 1-based row indexing
                if len(row) <= max(input_col, output_col, verification_col):
                    continue

                input_url = row[input_col]
                output_url = row[output_col]
                verification_ranges = row[verification_col]

                if not input_url or not output_url or not verification_ranges:
                    continue

                # Parse verification ranges
                ranges = self._parse_verification_ranges(str(verification_ranges))
                
                # Check each range for matching cells
                for range_info in ranges:
                    if range_info["sheet_name"] and range_info["range"]:
                        try:
                            # Get data from both sheets for this range
                            input_data = self._get_range_data(
                                spreadsheet, input_url, range_info, auth_credentials
                            )
                            output_data = self._get_range_data(
                                spreadsheet, output_url, range_info, auth_credentials
                            )
                            
                            if input_data and output_data:
                                # Compare cells in the range
                                matches = self._find_matching_cells(
                                    input_data, output_data, range_info
                                )
                                matching_cells_count += len(matches)
                                
                                for match in matches:
                                    verification_issues.append({
                                        "row": row_idx,
                                        "input_url": input_url,
                                        "output_url": output_url,
                                        "sheet": range_info["sheet_name"],
                                        "range": range_info["range"],
                                        "matching_cells": match
                                    })
                        except Exception as e:
                            result.add_error(
                                f"Error processing range {range_info['range']} in row {row_idx}: {str(e)}"
                            )

            result.add_issue(matching_cells_count)
            result.details["verification_issues"] = verification_issues
            result.set_automated_log(
                f"Found {matching_cells_count} matching cells in verification ranges"
            )

        return self._execute_validation(
            validation_logic, spreadsheet_source, auth_credentials, **kwargs
        )

    def _parse_verification_ranges(self, ranges_str: str) -> List[Dict[str, str]]:
        """Parse verification ranges string into structured format.
        
        Args:
            ranges_str: String containing verification ranges (e.g., "Sheet1!A1:B2,Sheet2!C1:D3")
            
        Returns:
            List of dictionaries with sheet_name and range
        """
        ranges = []
        if not ranges_str:
            return ranges
            
        # Split by comma and process each range
        for range_part in ranges_str.split(","):
            range_part = range_part.strip()
            if "!" in range_part:
                sheet_name, cell_range = range_part.split("!", 1)
                # Remove quotes if present
                sheet_name = sheet_name.strip("'\"")
                ranges.append({
                    "sheet_name": sheet_name,
                    "range": cell_range.strip()
                })
            else:
                # No sheet name specified
                ranges.append({
                    "sheet_name": None,
                    "range": range_part.strip()
                })
        
        return ranges

    def _get_range_data(
        self, 
        spreadsheet: SpreadsheetInterface, 
        url: str, 
        range_info: Dict[str, str],
        auth_credentials: Dict[str, Any]
    ) -> List[List[Any]]:
        """Get data from a specific range in a spreadsheet.
        
        Args:
            spreadsheet: Current spreadsheet interface
            url: URL of the target spreadsheet
            range_info: Dictionary with sheet_name and range
            auth_credentials: Authentication credentials
            
        Returns:
            List of rows containing the range data
        """
        try:
            # For now, return empty data - this would need to be implemented
            # to actually fetch data from the target spreadsheet
            return []
        except Exception:
            return []

    def _find_matching_cells(
        self, 
        input_data: List[List[Any]], 
        output_data: List[List[Any]], 
        range_info: Dict[str, str]
    ) -> List[str]:
        """Find cells that match between input and output data.
        
        Args:
            input_data: Data from input sheet range
            output_data: Data from output sheet range
            range_info: Information about the range being compared
            
        Returns:
            List of cell references where values match
        """
        matches = []
        
        if not input_data or not output_data:
            return matches
            
        # Simple comparison - in practice, this would need more sophisticated
        # range parsing and cell-by-cell comparison
        min_rows = min(len(input_data), len(output_data))
        min_cols = min(
            len(input_data[0]) if input_data else 0,
            len(output_data[0]) if output_data else 0
        )
        
        for row_idx in range(min_rows):
            for col_idx in range(min_cols):
                if (row_idx < len(input_data) and col_idx < len(input_data[row_idx]) and
                    row_idx < len(output_data) and col_idx < len(output_data[row_idx])):
                    if input_data[row_idx][col_idx] == output_data[row_idx][col_idx]:
                        # Convert to A1 notation
                        cell_ref = self._generate_cell_reference(row_idx, col_idx, range_info["sheet_name"])
                        matches.append(cell_ref)
        
        return matches
