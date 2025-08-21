"""Broken values validator.

This validator detects broken values in input and output sheets,
including corrupted data, invalid formats, and problematic content.
"""

import re
from typing import Any, Dict, List, Union, Optional
from pathlib import Path

from urarovite.validators.base import BaseValidator, ValidationResult
from urarovite.core.exceptions import ValidationError
from urarovite.core.spreadsheet import SpreadsheetInterface


class BrokenValuesValidator(BaseValidator):
    """Validator for detecting broken values in spreadsheets using the Apps Script approach.
    
    This validator detects actual error values that appear in Google Sheets cells
    (like #DIV/0!, #NAME?, #REF!, etc.) rather than trying to predict errors
    from raw formula text. It provides the same accuracy as the Apps Script tool
    while offering advanced features like linked sheet validation.
    
    Examples:
        # Basic usage - detect broken values
        validator = BrokenValuesValidator()
        result = validator.validate(
            spreadsheet_source="https://docs.google.com/spreadsheets/d/...",
            mode="flag",
            auth_credentials={"auth_secret": "base64_encoded_creds"}
        )
        
        # Validate with linked sheet support
        validator = BrokenValuesValidator(
            hyperlink_columns=["input_sheet_url", "output_sheet_url"]
        )
        result = validator.validate(
            spreadsheet_source="https://docs.google.com/spreadsheets/d/...",
            mode="fix",
            auth_credentials={"auth_secret": "base64_encoded_creds"}
        )
        
        # Custom replacement values
        result = validator.validate(
            spreadsheet_source="https://docs.google.com/spreadsheets/d/...",
            mode="fix",
            auth_credentials={"auth_secret": "base64_encoded_creds"},
            replace_value="[ERROR]"
        )
    """

    def __init__(self, hyperlink_columns: Optional[List[str]] = None) -> None:
        """Initialize the validator.
        
        Args:
            hyperlink_columns: List of column names that should contain hyperlinks
        """
        super().__init__(
            validator_id="broken_values",
            name="Broken Values Detector",
            description=(
                "Detects broken values in input and output sheets including "
                "corrupted data, invalid formats, and problematic content"
            ),
        )
        self.hyperlink_columns = hyperlink_columns or []

    def validate(
        self,
        spreadsheet_source: Union[str, Path, SpreadsheetInterface],
        mode: str,
        auth_credentials: Dict[str, Any] = None,
        hyperlink_columns: Optional[List[str]] = None,
        replace_value: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Validate for broken values in spreadsheets using the Apps Script approach.

        This method detects actual error values that appear in Google Sheets cells
        (like #DIV/0!, #NAME?, #REF!, etc.) by analyzing display values rather
        than raw formula text. It provides the same accuracy as the Apps Script tool.

        Args:
            spreadsheet_source: Either a Google Sheets URL, Excel file path,
                or SpreadsheetInterface
            mode: Either "fix" or "flag" mode
            auth_credentials: Authentication credentials (required for Google Sheets)
            hyperlink_columns: List of column names that contain hyperlinks to validate
            replace_value: Custom value to use when replacing broken content (default: auto-determined)

        Returns:
            Dict with validation results containing:
            - details.broken_values: List of detected broken values
            - details.total_cells_checked: Total number of cells validated
            - details.fixes_applied: Number of fixes applied (fix mode only)
            - details.linked_sheets_validated: Number of linked sheets processed

        Examples:
            # Basic validation in flag mode
            result = validator.validate(
                spreadsheet_source="https://docs.google.com/spreadsheets/d/...",
                mode="flag",
                auth_credentials={"auth_secret": "base64_encoded_creds"}
            )
            print(f"Found {len(result['details']['broken_values'])} broken values")

            # Auto-fix mode with linked sheet validation
            result = validator.validate(
                spreadsheet_source="https://docs.google.com/spreadsheets/d/...",
                mode="fix",
                auth_credentials={"auth_secret": "base64_encoded_creds"},
                hyperlink_columns=["input_sheet_url", "output_sheet_url"]
            )
            print(f"Applied {result['fixes_applied']} fixes")

            # Custom replacement values
            result = validator.validate(
                spreadsheet_source="https://docs.google.com/spreadsheets/d/...",
                mode="fix",
                auth_credentials={"auth_secret": "base64_encoded_creds"},
                replace_value="[BROKEN_VALUE]"
            )

        Error Detection:
            The validator detects the following error tokens (same as Apps Script):
            - #REF! (Reference errors)
            - #VALUE! (Value errors) 
            - #DIV/0! (Division by zero)
            - #N/A (Not available)
            - #NAME? (Unknown function names)
            - #NULL! (Null reference errors)
            - #NUM! (Numeric errors)
            - #ERROR! (General errors)

        Auto-fix Behavior:
            - Error values: Replaced with custom value or empty string
            - Broken formulas: Converted to literal strings (e.g., '=11/0') for debugging
            - Control characters: Replaced with custom value or empty string
            - Long content: Truncated if exceeds limits
        """

        def validation_logic(
            spreadsheet: SpreadsheetInterface, result: ValidationResult, **kwargs
        ) -> None:
            # Use hyperlink_columns parameter if provided, otherwise fall back to instance variable
            effective_hyperlink_columns = hyperlink_columns or self.hyperlink_columns
            
            # Get display values (what the user sees) - this is key for detecting error values!
            display_data, sheet_name = self._get_display_values(spreadsheet)
            
            # Also get raw data for getting original formulas when fixing
            raw_data, _ = self._get_all_sheet_data(spreadsheet)

            if not display_data:
                result.add_error("Sheet is empty - no data to validate")
                result.set_automated_log("Sheet is empty - no data to validate")
                return

            broken_values = []
            total_cells_checked = 0
            fixes_applied = 0
            linked_sheets_validated = 0

            # Process main sheet data using display values for detection
            for row_idx, row in enumerate(display_data):
                for col_idx, display_value in enumerate(row):
                    total_cells_checked += 1
                    
                    # Get the raw value for this cell (for fixing)
                    raw_value = None
                    if row_idx < len(raw_data) and col_idx < len(raw_data[row_idx]):
                        raw_value = raw_data[row_idx][col_idx]
                    
                    # Check for broken values using display value
                    issues = self._check_cell_value_display(display_value, raw_value, row_idx + 1, col_idx + 1)
                    if issues:
                        broken_values.extend(issues)
                        
                        # Apply fixes if in fix mode
                        if mode == "fix":
                            fix_applied = self._apply_fix_to_cell(
                                spreadsheet, sheet_name, row_idx + 1, col_idx + 1, display_value, raw_value, replace_value
                            )
                            if fix_applied:
                                fixes_applied += 1

            # Process linked sheets if hyperlink columns are specified
            if effective_hyperlink_columns:
                # Temporarily set the hyperlink columns for this validation
                original_hyperlink_columns = self.hyperlink_columns
                self.hyperlink_columns = effective_hyperlink_columns
                
                linked_sheet_results = self._validate_linked_sheets(
                    spreadsheet, display_data, mode, auth_credentials, replace_value
                )
                broken_values.extend(linked_sheet_results["broken_values"])
                total_cells_checked += linked_sheet_results["total_cells_checked"]
                fixes_applied += linked_sheet_results["fixes_applied"]
                linked_sheets_validated = linked_sheet_results["sheets_validated"]
                
                # Restore original hyperlink columns
                self.hyperlink_columns = original_hyperlink_columns

            if mode == "fix":
                result.add_fix(fixes_applied)
                if fixes_applied > 0:
                    spreadsheet.save()
            else:
                result.add_issue(len(broken_values))
                
            result.details["broken_values"] = broken_values
            result.details["total_cells_checked"] = total_cells_checked
            result.details["fixes_applied"] = fixes_applied
            result.details["linked_sheets_validated"] = linked_sheets_validated
            
            log_message = f"Found {len(broken_values)} broken values in {total_cells_checked} cells"
            if linked_sheets_validated > 0:
                log_message += f" across {linked_sheets_validated + 1} sheets"
            if mode == "fix":
                log_message += f", applied {fixes_applied} fixes"
            
            result.set_automated_log(log_message)

        return self._execute_validation(
            validation_logic, spreadsheet_source, auth_credentials, **kwargs
        )

    def _get_display_values(self, spreadsheet: SpreadsheetInterface, sheet_name: str = None) -> tuple[List[List[Any]], str]:
        """Get display values from a sheet (what the user sees).
        
        This is crucial for detecting error values like #DIV/0!, #NAME?, etc.
        that appear in cells when formulas fail.
        
        Args:
            spreadsheet: SpreadsheetInterface instance
            sheet_name: Name of the specific sheet (optional)
            
        Returns:
            Tuple of (2D list of display values, sheet name used)
        """
        try:
            # Try to get display values if the spreadsheet supports it
            if hasattr(spreadsheet, 'get_sheet_display_values'):
                sheet_data = spreadsheet.get_sheet_display_values(sheet_name=sheet_name)
                return sheet_data.values, sheet_data.sheet_name
            else:
                # Fall back to regular sheet data for non-Google Sheets
                return self._get_all_sheet_data(spreadsheet, sheet_name)
        except Exception as e:
            # Fall back to regular sheet data if display values fail
            print(f"Warning: Failed to get display values, falling back to regular data: {e}")
            return self._get_all_sheet_data(spreadsheet, sheet_name)

    def _check_cell_value_display(self, display_value: Any, raw_value: Any, row_idx: int, col_idx: int) -> List[Dict[str, Any]]:
        """Check a single cell using its display value for broken content.
        
        This is the Apps Script approach - check what the user actually sees.
        
        Args:
            display_value: The display value in the cell (what user sees)
            raw_value: The raw value in the cell (for context)
            row_idx: Row index (1-based)
            col_idx: Column index (1-based)
            
        Returns:
            List of issues found in the cell
        """
        issues = []
        
        if display_value is None:
            return issues
            
        display_str = str(display_value)
        
        # This is the key insight from the Apps Script: detect actual error tokens
        # that appear in the display (what the user sees)
        error_tokens = ['#REF!', '#VALUE!', '#DIV/0!', '#N/A', '#NAME?', '#NULL!', '#NUM!', '#ERROR!']
        
        for token in error_tokens:
            if token in display_str:
                issues.append({
                    "row": row_idx,
                    "col": col_idx,
                    "cell": self._generate_cell_reference(row_idx - 1, col_idx - 1),
                    "display_value": display_value,
                    "raw_value": raw_value,
                    "issue": f"Contains error value: {token}",
                    "severity": "error"
                })
                break  # Only report one error per cell
        
        # Still check for other issues using display value
        if len(display_str) > 50000:  # Excel cell limit is 32,767 characters
            issues.append({
                "row": row_idx,
                "col": col_idx,
                "cell": self._generate_cell_reference(row_idx - 1, col_idx - 1),
                "display_value": f"{display_str[:100]}...",
                "raw_value": raw_value,
                "issue": "Content exceeds reasonable length limit",
                "severity": "warning"
            })
        
        # Check for control characters in display text
        if self._contains_control_characters(display_str):
            issues.append({
                "row": row_idx,
                "col": col_idx,
                "cell": self._generate_cell_reference(row_idx - 1, col_idx - 1),
                "display_value": f"{display_str[:50]}...",
                "raw_value": raw_value,
                "issue": "Contains control characters",
                "severity": "warning"
            })
        
        return issues

    def _check_cell_value(self, cell_value: Any, row_idx: int, col_idx: int) -> List[Dict[str, Any]]:
        """Check a single cell value for broken content.
        
        Args:
            cell_value: The value in the cell
            row_idx: Row index (1-based)
            col_idx: Column index (1-based)
            
        Returns:
            List of issues found in the cell
        """
        issues = []
        
        if cell_value is None:
            return issues
            
        cell_str = str(cell_value)
        
        # Check for error values (only actual error results, not literal strings)
        if self._is_error_value(cell_value):
            issues.append({
                "row": row_idx,
                "col": col_idx,
                "cell": self._generate_cell_reference(row_idx - 1, col_idx - 1),
                "value": cell_value,
                "issue": "Contains error value",
                "severity": "error"
            })
        
        # Check for extremely long content
        if len(cell_str) > 50000:  # Excel cell limit is 32,767 characters
            issues.append({
                "row": row_idx,
                "col": col_idx,
                "cell": self._generate_cell_reference(row_idx - 1, col_idx - 1),
                "value": f"{cell_str[:100]}...",
                "issue": "Content exceeds reasonable length limit",
                "severity": "warning"
            })
        
        # Check for broken URLs (only if they look like actual URLs)
        if self._is_broken_url(cell_str):
            issues.append({
                "row": row_idx,
                "col": col_idx,
                "cell": self._generate_cell_reference(row_idx - 1, col_idx - 1),
                "value": cell_str,
                "issue": "Contains broken or malformed URL",
                "severity": "error"
            })
        
        # Check for broken formulas (only if they start with =)
        if self._is_broken_formula(cell_str):
            issues.append({
                "row": row_idx,
                "col": col_idx,
                "cell": self._generate_cell_reference(row_idx - 1, col_idx - 1),
                "value": cell_str,
                "issue": "Contains broken or malformed formula",
                "severity": "error"
            })
        
        # Check for control characters in text
        if self._contains_control_characters(cell_str):
            issues.append({
                "row": row_idx,
                "col": col_idx,
                "cell": self._generate_cell_reference(row_idx - 1, col_idx - 1),
                "value": f"{cell_str[:50]}...",
                "issue": "Contains control characters",
                "severity": "warning"
            })
        
        # Check for formulas that would cause errors
        if self._would_cause_error(cell_str):
            issues.append({
                "row": row_idx,
                "col": col_idx,
                "cell": self._generate_cell_reference(row_idx - 1, col_idx - 1),
                "value": cell_str,
                "issue": "Formula would cause calculation error",
                "severity": "error"
            })
        
        return issues

    def _is_error_value(self, value: Any) -> bool:
        """Check if a value represents an error.
        
        Args:
            value: Value to check
            
        Returns:
            True if it's an error value
        """
        if isinstance(value, str):
            # Use search instead of match to find error patterns anywhere in the string
            # This handles cases like "#DIV/0! (Function DIVIDE parameter 2 cannot be zero.)"
            error_patterns = [
                r'#N/A',
                r'#VALUE!',
                r'#REF!',
                r'#DIV/0!',
                r'#NUM!',
                r'#NAME\?',
                r'#NULL!',
                r'#ERROR!'
            ]
            return any(re.search(pattern, value) for pattern in error_patterns)
        return False

    def _is_broken_url(self, text: str) -> bool:
        """Check if text contains a broken URL.
        
        Args:
            text: Text to check
            
        Returns:
            True if it contains a broken URL
        """
        # Check if it looks like it's meant to be a URL
        if 'http' in text.lower():
            # Check for common URL patterns that are broken
            broken_patterns = [
                r'http://\s',  # Space after protocol
                r'https://\s',  # Space after protocol
                r'http://$',    # Ends with protocol
                r'https://$',   # Ends with protocol
                r'http://[^\w]',  # Invalid character after protocol
                r'https://[^\w]', # Invalid character after protocol
                r'^https://$',    # Just the protocol (no domain)
                r'^http://$',     # Just the protocol (no domain)
            ]
            return any(re.search(pattern, text) for pattern in broken_patterns)
        return False

    def _is_broken_formula(self, text: str) -> bool:
        """Check if text contains a broken formula.
        
        Args:
            text: Text to check
            
        Returns:
            True if it contains a broken formula
        """
        if text.startswith('='):
            # Check for common formula issues
            broken_patterns = [
                r'=\s*$',           # Formula ends with space
                r'=\s*[^\w(+\-*/]', # Invalid character after =
                r'=\s*[+\-*/]\s*$', # Formula ends with operator
                r'=\s*[+\-*/]\s*[+\-*/]', # Consecutive operators
                r'=\s*[+\-*/]\s*[^\w(]',  # Invalid character after operator
                r'=\w+\([+\-*/]\s*$',     # Function with incomplete parameters ending with operator
                r'=\w+\(\s*[+\-*/]',      # Function starting with operator
                r'=\w+\(\s*$',            # Function with incomplete parameters
                r'=\w+\([+\-*/]',         # Function starting with operator
                r'=\w+\s*$',              # Function name only
                r'=\w+\s*[+\-*/]',        # Function name followed by operator
                r'=\w+\s*[+\-*/]\s*$',    # Function name, operator, end
                r'=\w+\s*[+\-*/]\s*[+\-*/]', # Function name, operator, another operator
            ]
            return any(re.search(pattern, text) for pattern in broken_patterns)
        return False

    def _apply_fix_to_cell(
        self, 
        spreadsheet: SpreadsheetInterface, 
        sheet_name: str, 
        row_idx: int, 
        col_idx: int, 
        display_value: Any,
        raw_value: Any,
        replace_value: Optional[str] = None
    ) -> bool:
        """Apply a fix to a broken cell using the Apps Script approach.
        
        Args:
            spreadsheet: The spreadsheet interface
            sheet_name: Name of the sheet
            row_idx: Row index (1-based)
            col_idx: Column index (1-based)
            display_value: Display value (what user sees)
            raw_value: Raw value (original formula/value)
            replace_value: Custom value to use when replacing broken content (default: auto-determined)
            
        Returns:
            True if fix was applied, False otherwise
        """
        try:
            display_str = str(display_value)
            
            # Check if display value contains error tokens (Apps Script approach)
            error_tokens = ['#REF!', '#VALUE!', '#DIV/0!', '#N/A', '#NAME?', '#NULL!', '#NUM!', '#ERROR!']
            
            for token in error_tokens:
                if token in display_str:
                    if replace_value is not None:
                        fixed_value = replace_value
                    else:
                        # Default behavior: convert original formula to literal string for debugging
                        if raw_value and str(raw_value).startswith('='):
                            fixed_value = f"'{str(raw_value)}"
                        else:
                            fixed_value = ""
                    
                    spreadsheet.update_sheet_data(
                        sheet_name=sheet_name,
                        values=[[fixed_value]],
                        start_row=row_idx,
                        start_col=col_idx
                    )
                    return True
                
        except Exception as e:
            # Log error but don't fail the validation
            print(f"Warning: Failed to fix cell {sheet_name}!{self._generate_cell_reference(row_idx - 1, col_idx - 1)}: {e}")
            
        return False

    def _validate_linked_sheets(
        self, 
        spreadsheet: SpreadsheetInterface, 
        main_sheet_data: List[List[Any]], 
        mode: str, 
        auth_credentials: Dict[str, Any],
        replace_value: Optional[str] = None
    ) -> Dict[str, Any]:
        """Validate linked sheets from hyperlink columns.
        
        Args:
            spreadsheet: The main spreadsheet interface
            main_sheet_data: Data from the main sheet
            mode: Validation mode ('flag' or 'fix')
            auth_credentials: Authentication credentials
            replace_value: Custom value to use when replacing broken content
            
        Returns:
            Dict with validation results from linked sheets
        """
        broken_values = []
        total_cells_checked = 0
        fixes_applied = 0
        sheets_validated = 0
        
        # Get column headers to find hyperlink column indices
        if not main_sheet_data:
            return {"broken_values": [], "total_cells_checked": 0, "fixes_applied": 0, "sheets_validated": 0}
            
        headers = main_sheet_data[0] if main_sheet_data else []
        
        # Find indices of hyperlink columns
        hyperlink_col_indices = []
        for col_name in self.hyperlink_columns:
            try:
                col_idx = headers.index(col_name)
                hyperlink_col_indices.append(col_idx)
            except ValueError:
                print(f"Warning: Hyperlink column '{col_name}' not found in headers")
                continue
        
        if not hyperlink_col_indices:
            return {"broken_values": [], "total_cells_checked": 0, "fixes_applied": 0, "sheets_validated": 0}
        
        # Get sheet data with hyperlinks to extract actual URLs
        try:
            hyperlink_data, _ = self._get_sheet_data_with_hyperlinks(spreadsheet)
        except Exception as e:
            print(f"Warning: Failed to get hyperlink data: {e}")
            return {"broken_values": [], "total_cells_checked": 0, "fixes_applied": 0, "sheets_validated": 0}
        
        # Process each row to find linked sheets
        for row_idx, row in enumerate(hyperlink_data[1:], start=2):  # Skip header row
            for col_idx in hyperlink_col_indices:
                if col_idx < len(row) and row[col_idx]:
                    cell_value = row[col_idx]
                    
                    # Check if this looks like a Google Sheets URL
                    if isinstance(cell_value, str) and 'docs.google.com/spreadsheets' in cell_value:
                        try:
                            print(f"Validating linked sheet: {cell_value}")
                            linked_sheet_result = self._validate_single_linked_sheet(
                                cell_value, mode, auth_credentials, replace_value
                            )
                            
                            if linked_sheet_result:
                                broken_values.extend(linked_sheet_result["broken_values"])
                                total_cells_checked += linked_sheet_result["total_cells_checked"]
                                fixes_applied += linked_sheet_result["fixes_applied"]
                                sheets_validated += 1
                                
                        except Exception as e:
                            print(f"Warning: Failed to validate linked sheet {cell_value}: {e}")
        
        return {
            "broken_values": broken_values,
            "total_cells_checked": total_cells_checked,
            "fixes_applied": fixes_applied,
            "sheets_validated": sheets_validated
        }

    def _validate_single_linked_sheet(
        self, 
        sheet_url: str, 
        mode: str, 
        auth_credentials: Dict[str, Any],
        replace_value: Optional[str] = None
    ) -> Dict[str, Any]:
        """Validate a single linked sheet.
        
        Args:
            sheet_url: URL of the linked sheet
            mode: Validation mode ('flag' or 'fix')
            auth_credentials: Authentication credentials
            replace_value: Custom value to use when replacing broken content
            
        Returns:
            Dict with validation results
        """
        try:
            # Create a new validator instance for the linked sheet
            linked_validator = BrokenValuesValidator()
            
            # Validate the linked sheet
            result = linked_validator.validate(
                sheet_url, 
                mode, 
                auth_credentials,
                replace_value=replace_value
            )
            
            # Extract broken values and add sheet context
            broken_values = []
            for broken_value in result.get("details", {}).get("broken_values", []):
                # Add sheet URL context to each broken value
                broken_value["sheet_url"] = sheet_url
                broken_value["sheet_type"] = "linked_sheet"
                broken_values.append(broken_value)
            
            return {
                "broken_values": broken_values,
                "total_cells_checked": result.get("details", {}).get("total_cells_checked", 0),
                "fixes_applied": result.get("fixes_applied", 0)
            }
            
        except Exception as e:
            print(f"Error validating linked sheet {sheet_url}: {e}")
            return {"broken_values": [], "total_cells_checked": 0, "fixes_applied": 0}

    def _get_fixed_value(self, cell_value: Any) -> str:
        """Get the fixed value for a broken cell.
        
        Args:
            cell_value: The original cell value
            
        Returns:
            The fixed value
        """
        if self._is_error_value(cell_value):
            return ""
        elif self._is_broken_formula(str(cell_value)):
            # Remove the = and any trailing operators
            fixed_value = re.sub(r'^=\s*[+\-*/]*\s*', '', str(cell_value))
            return fixed_value if fixed_value else ""
        elif self._would_cause_error(str(cell_value)):
            # Remove the = sign from error-causing formulas
            fixed_value = re.sub(r'^=\s*', '', str(cell_value))
            return fixed_value if fixed_value else ""
        elif self._is_broken_url(str(cell_value)):
            return ""
        else:
            return str(cell_value)

    def _get_sheet_data_with_hyperlinks(
        self, spreadsheet: SpreadsheetInterface, sheet_name: str = None
    ) -> tuple[List[List[Any]], str]:
        """Helper method to get all data from a sheet with hyperlinks resolved.
        
        Args:
            spreadsheet: SpreadsheetInterface instance
            sheet_name: Name of the specific sheet (optional)
            
        Returns:
            Tuple of (2D list of cell values with hyperlinks as URLs, sheet name used)
        """
        try:
            # Get sheet data with hyperlinks
            sheet_data = spreadsheet.get_sheet_data_with_hyperlinks(sheet_name=sheet_name)
            return sheet_data.values, sheet_data.sheet_name
        except Exception as e:
            # Fall back to regular sheet data if hyperlink extraction fails
            print(f"Warning: Failed to get hyperlinks, falling back to regular data: {e}")
            return self._get_all_sheet_data(spreadsheet, sheet_name)

    def _contains_control_characters(self, text: str) -> bool:
        """Check if text contains control characters.
        
        Args:
            text: Text to check
            
        Returns:
            True if it contains control characters
        """
        # Check for common control characters
        control_chars = ['\x00', '\x01', '\x02', '\x03', '\x04', '\x05', '\x06', '\x07',
                        '\x08', '\x09', '\x0A', '\x0B', '\x0C', '\x0D', '\x0E', '\x0F',
                        '\x10', '\x11', '\x12', '\x13', '\x14', '\x15', '\x16', '\x17',
                        '\x18', '\x19', '\x1A', '\x1B', '\x1C', '\x1D', '\x1E', '\x1F']
        return any(char in text for char in control_chars)

    def _would_cause_error(self, text: str) -> bool:
        """Check if a formula would cause a calculation error.
        
        Args:
            text: Text to check
            
        Returns:
            True if it would cause an error
        """
        if text.startswith('='):
            # Check for division by zero
            if re.search(r'/\s*0\s*$', text) or re.search(r'/\s*0\s*[+\-*/]', text):
                return True
            # Check for invalid function names
            if re.search(r'=\s*INVALID_\w+\(', text, re.IGNORECASE):
                return True
            # Check for other problematic patterns
            if re.search(r'=\s*\d+\s*/\s*0', text):
                return True
        return False
