"""Format compatibility validator.

This validator checks for compatibility issues between Google Sheets and Excel files,
detecting broken references and format-specific problems.
"""

import re
from typing import Any, Dict, List, Union
from pathlib import Path

from urarovite.validators.base import BaseValidator, ValidationResult
from urarovite.core.exceptions import ValidationError
from urarovite.core.spreadsheet import SpreadsheetInterface


class FormatCompatibilityValidator(BaseValidator):
    """Validator for checking Google Sheets/Excel compatibility issues."""

    def __init__(self) -> None:
        super().__init__(
            validator_id="format_compatibility",
            name="Format Compatibility Checker",
            description=(
                "Detects compatibility issues between Google Sheets and Excel files, "
                "including broken references and format-specific problems"
            ),
        )

    def validate(
        self,
        spreadsheet_source: Union[str, Path, SpreadsheetInterface],
        mode: str,
        auth_credentials: Dict[str, Any] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Validate format compatibility between Google Sheets and Excel.

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

            # Find columns containing file URLs
            input_col = None
            output_col = None
            excel_input_col = None
            excel_output_col = None

            # Look for header row to identify columns
            if data:
                header_row = data[0]
                for col_idx, header in enumerate(header_row):
                    header_str = str(header).lower().strip()
                    if ("input" in header_str and ("file" in header_str or "sheet" in header_str or "url" in header_str) and "excel" not in header_str):
                        input_col = col_idx
                    elif ("output" in header_str and ("file" in header_str or "sheet" in header_str or "url" in header_str) and "excel" not in header_str):
                        output_col = col_idx
                    elif "input" in header_str and "excel" in header_str:
                        excel_input_col = col_idx
                    elif "output" in header_str and "excel" in header_str:
                        excel_output_col = col_idx

            compatibility_issues = []
            broken_references = []

            # Check if we have any relevant columns
            relevant_cols = [col for col in [input_col, output_col, excel_input_col, excel_output_col] if col is not None]
            if not relevant_cols:
                result.add_error("No relevant file columns found")
                result.set_automated_log("No relevant file columns found")
                return

            max_col = max(relevant_cols)

            # Process each row (skip header)
            for row_idx, row in enumerate(data[1:], start=2):  # 1-based row indexing
                if len(row) <= max_col:
                    continue

                # Check Google Sheets URLs
                if input_col is not None and input_col < len(row):
                    input_url = row[input_col]
                    if input_url and self._is_google_sheets_url(input_url):
                        issues = self._check_google_sheets_compatibility(
                            input_url, "Input", row_idx, auth_credentials
                        )
                        compatibility_issues.extend(issues)

                if output_col is not None and output_col < len(row):
                    output_url = row[output_col]
                    if output_url and self._is_google_sheets_url(output_url):
                        issues = self._check_google_sheets_compatibility(
                            output_url, "Output", row_idx, auth_credentials
                        )
                        compatibility_issues.extend(issues)

                # Check Excel files
                if excel_input_col is not None and excel_input_col < len(row):
                    excel_input = row[excel_input_col]
                    if excel_input:
                        issues = self._check_excel_compatibility(
                            excel_input, "Excel Input", row_idx
                        )
                        compatibility_issues.extend(issues)

                if excel_output_col is not None and excel_output_col < len(row):
                    excel_output = row[excel_output_col]
                    if excel_output:
                        issues = self._check_excel_compatibility(
                            excel_output, "Excel Output", row_idx
                        )
                        compatibility_issues.extend(issues)

                # Check for broken references in verification ranges
                verification_col = None
                for col_idx, header in enumerate(header_row):
                    header_str = str(header).lower().strip()
                    if "verification" in header_str and "range" in header_str:
                        verification_col = col_idx
                        break

                if verification_col is not None and verification_col < len(row):
                    verification_ranges = row[verification_col]
                    if verification_ranges:
                        broken_refs = self._check_broken_references(
                            str(verification_ranges), row_idx
                        )
                        broken_references.extend(broken_refs)

            result.add_issue(len(compatibility_issues) + len(broken_references))
            result.details["compatibility_issues"] = compatibility_issues
            result.details["broken_references"] = broken_references
            result.set_automated_log(
                f"Found {len(compatibility_issues)} compatibility issues and {len(broken_references)} broken references"
            )

        return self._execute_validation(
            validation_logic, spreadsheet_source, auth_credentials, **kwargs
        )

    def _is_google_sheets_url(self, url: str) -> bool:
        """Check if a URL is a Google Sheets URL.
        
        Args:
            url: URL to check
            
        Returns:
            True if it's a Google Sheets URL
        """
        return "docs.google.com/spreadsheets" in url

    def _check_google_sheets_compatibility(
        self, url: str, file_type: str, row_idx: int, auth_credentials: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Check Google Sheets compatibility issues.
        
        Args:
            url: Google Sheets URL
            file_type: Type of file (Input/Output)
            row_idx: Row number
            auth_credentials: Authentication credentials
            
        Returns:
            List of compatibility issues
        """
        issues = []
        
        try:
            # Check if URL is accessible
            if not auth_credentials:
                issues.append({
                    "row": row_idx,
                    "file_type": file_type,
                    "url": url,
                    "issue": "No authentication credentials provided",
                    "severity": "warning"
                })
            else:
                # In a real implementation, we would try to access the sheet
                # and check for specific compatibility issues
                issues.append({
                    "row": row_idx,
                    "file_type": file_type,
                    "url": url,
                    "issue": "Google Sheets URL detected - check for broken references after conversion",
                    "severity": "info"
                })
        except Exception as e:
            issues.append({
                "row": row_idx,
                "file_type": file_type,
                "url": url,
                "issue": f"Error checking compatibility: {str(e)}",
                "severity": "error"
            })
        
        return issues

    def _check_excel_compatibility(self, file_path: str, file_type: str, row_idx: int) -> List[Dict[str, Any]]:
        """Check Excel file compatibility issues.
        
        Args:
            file_path: Path to Excel file
            file_type: Type of file (Excel Input/Excel Output)
            row_idx: Row number
            
        Returns:
            List of compatibility issues
        """
        issues = []
        
        try:
            # Check if file exists and is accessible
            path = Path(file_path)
            if not path.exists():
                issues.append({
                    "row": row_idx,
                    "file_type": file_type,
                    "file_path": file_path,
                    "issue": "Excel file not found",
                    "severity": "error"
                })
            elif not path.suffix.lower() in ['.xlsx', '.xls']:
                issues.append({
                    "row": row_idx,
                    "file_type": file_type,
                    "file_path": file_path,
                    "issue": "File is not a valid Excel format",
                    "severity": "warning"
                })
            else:
                issues.append({
                    "row": row_idx,
                    "file_type": file_type,
                    "file_path": file_path,
                    "issue": "Excel file detected - check for broken references after conversion to Google Sheets",
                    "severity": "info"
                })
        except Exception as e:
            issues.append({
                "row": row_idx,
                "file_type": file_type,
                "file_path": file_path,
                "issue": f"Error checking Excel compatibility: {str(e)}",
                "severity": "error"
            })
        
        return issues

    def _check_broken_references(self, verification_ranges: str, row_idx: int) -> List[Dict[str, Any]]:
        """Check for broken references in verification ranges.
        
        Args:
            verification_ranges: String containing verification ranges
            row_idx: Row number
            
        Returns:
            List of broken reference issues
        """
        broken_refs = []
        
        # Parse ranges and check for common issues
        ranges = verification_ranges.split(",")
        for range_part in ranges:
            range_part = range_part.strip()
            if "!" in range_part:
                sheet_name, cell_range = range_part.split("!", 1)
                sheet_name = sheet_name.strip("'\"")
                
                # Check for common issues
                if len(sheet_name) > 31:
                    broken_refs.append({
                        "row": row_idx,
                        "range": range_part,
                        "issue": f"Sheet name '{sheet_name}' exceeds 31 character limit",
                        "severity": "error"
                    })
                
                # Check for invalid characters in sheet names
                if not re.match(r'^[a-zA-Z0-9\s]+$', sheet_name):
                    broken_refs.append({
                        "row": row_idx,
                        "range": range_part,
                        "issue": f"Sheet name '{sheet_name}' contains invalid characters",
                        "severity": "error"
                    })
                
                # Check for malformed cell ranges
                if not re.match(r'^[A-Z]+\d+(?::[A-Z]+\d+)?$', cell_range):
                    broken_refs.append({
                        "row": row_idx,
                        "range": range_part,
                        "issue": f"Invalid cell range format: {cell_range}",
                        "severity": "error"
                    })
        
        return broken_refs
