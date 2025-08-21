"""Base validator class for all validation implementations.

This module defines the abstract base class that all validators must inherit
from, ensuring consistent interface and behavior across all validation checks.
"""

import logging
from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Any, Dict, List, Union, Optional, Iterator, Callable
from pathlib import Path

from urarovite.core.exceptions import ValidationError
from urarovite.core.spreadsheet import SpreadsheetInterface, SpreadsheetFactory


class ValidationResult:
    """Container for validation results."""

    def __init__(self) -> None:
        self.fixes_applied: int = 0
        self.flags_found: int = 0
        self.errors: List[str] = []
        self.details: Dict[str, Any] = {}
        self.automated_log: str = ""

    def add_fix(self, count: int = 1) -> None:
        """Add to the count of fixes applied."""
        self.fixes_applied += count

    def add_issue(self, count: int = 1) -> None:
        """Add to the count of flags found."""
        self.flags_found += count

    def add_error(self, error: str) -> None:
        """Add an error message."""
        self.errors.append(error)

    def add_detailed_issue(
        self, sheet_name: str, cell: str, message: str, value: Any = None
    ) -> None:
        """Add a detailed issue to be reported.

        Args:
            sheet_name: The name of the sheet where the issue was found.
            cell: The cell reference (e.g., "A1").
            message: A description of the issue.
            value: The problematic value in the cell.
        """
        if "flags" not in self.details:
            self.details["flags"] = []
        self.details["flags"].append(
            {"sheet": sheet_name, "cell": cell, "message": message, "value": value}
        )
        self.add_issue()

    def add_detailed_fix(
        self,
        sheet_name: str,
        cell: str,
        message: str,
        old_value: Any = None,
        new_value: Any = None,
    ) -> None:
        """Add a detailed fix to be reported.

        Args:
            sheet_name: The name of the sheet where the fix was applied.
            cell: The cell reference (e.g., "A1").
            message: A description of the fix.
            old_value: The original value before fixing.
            new_value: The new value after fixing.
        """
        if "fixes" not in self.details:
            self.details["fixes"] = []
        self.details["fixes"].append(
            {
                "sheet": sheet_name,
                "cell": cell,
                "message": message,
                "old_value": old_value,
                "new_value": new_value,
            }
        )
        self.add_fix()

    def set_automated_log(self, log: str) -> None:
        """Set the automated log message."""
        self.automated_log = log

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for API response."""
        return {
            "fixes_applied": self.fixes_applied,
            "flags_found": self.flags_found,
            "errors": self.errors,
            "details": self.details,
            "automated_log": self.automated_log,
        }


class BaseValidator(ABC):
    """Abstract base class for all validators.

    All validation implementations must inherit from this class and implement
    the required methods. This ensures consistent behavior and error handling.
    """

    def __init__(self, validator_id: str, name: str, description: str) -> None:
        """Initialize the validator.

        Args:
            validator_id: Unique identifier for this validator
            name: Human-readable name
            description: Description of what this validator does
        """
        self.id = validator_id
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"{__name__}.{validator_id}")

    @abstractmethod
    def validate(
        self,
        spreadsheet_source: Union[str, Path, SpreadsheetInterface],
        mode: str,
        auth_credentials: Dict[str, Any] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Execute the validation check.

        Args:
            spreadsheet_source: Either a Google Sheets URL, Excel file path,
                or SpreadsheetInterface
            mode: Either "fix" (auto-correct) or "flag" (report only)
            auth_credentials: Authentication credentials (required for
                Google Sheets)
            **kwargs: Additional validator-specific parameters

        Returns:
            Dict with validation results

        Raises:
            ValidationError: If validation fails
        """
        pass

    def _get_spreadsheet(
        self,
        spreadsheet_source: Union[str, Path, SpreadsheetInterface],
        auth_credentials: Dict[str, Any] = None,
        read_only: Optional[bool] = None,
    ) -> SpreadsheetInterface:
        """Helper method to get a spreadsheet interface with enhanced detection.

        This method leverages the enhanced SpreadsheetFactory to automatically:
        - Detect source type (local Excel, Google Sheets, Drive-hosted Excel)
        - Handle authentication centrally
        - Apply intelligent defaults based on source type

        Args:
            spreadsheet_source: Source identifier - can be:
                              - Local Excel file path
                              - Google Sheets URL
                              - Google Drive file URL or ID
                              - Existing SpreadsheetInterface instance
            auth_credentials: Authentication credentials (auto-determined if not provided)
            read_only: Whether to open in read-only mode (None = auto-detect based on operation)

        Returns:
            SpreadsheetInterface instance

        Raises:
            ValidationError: If unable to create spreadsheet interface
        """
        if isinstance(spreadsheet_source, SpreadsheetInterface):
            return spreadsheet_source

        # Enhanced parameter handling
        kwargs = {}
        if read_only is not None:
            kwargs["read_only"] = read_only

        # Use enhanced SpreadsheetFactory with dynamic detection
        try:
            return SpreadsheetFactory.create_spreadsheet(
                spreadsheet_source, auth_credentials, **kwargs
            )
        except ValidationError as e:
            # Enhance error message with validator context
            raise ValidationError(
                f"Failed to access spreadsheet in {self.id} validator: {str(e)}"
            )

    def _get_all_sheet_data(
        self, spreadsheet: SpreadsheetInterface, sheet_name: str = None
    ) -> tuple[List[List[Any]], str]:
        """Helper method to get all data from a sheet.

        Args:
            spreadsheet: SpreadsheetInterface instance
            sheet_name: Name of the specific sheet (optional)

        Returns:
            Tuple of (2D list of cell values, sheet name used)

        Raises:
            ValidationError: If unable to read sheet data
        """
        try:
            # Get sheet data
            sheet_data = spreadsheet.get_sheet_data(sheet_name=sheet_name)
            return sheet_data.values, sheet_data.sheet_name

        except Exception as e:
            raise ValidationError(f"Failed to get sheet data: {str(e)}")

    def _update_sheet_data(
        self,
        spreadsheet: SpreadsheetInterface,
        sheet_name: str,
        values: List[List[Any]],
        start_row: int = 1,
        start_col: int = 1,
    ) -> None:
        """Helper method to update sheet data.

        Args:
            spreadsheet: SpreadsheetInterface instance
            sheet_name: Name of the sheet to update
            values: 2D list of values to write
            start_row: Starting row (1-based)
            start_col: Starting column (1-based)

        Raises:
            ValidationError: If unable to update sheet
        """
        try:
            spreadsheet.update_sheet_data(
                sheet_name=sheet_name,
                values=values,
                start_row=start_row,
                start_col=start_col,
            )

        except Exception as e:
            raise ValidationError(f"Failed to update sheet data: {str(e)}")

    @contextmanager
    def _managed_spreadsheet(
        self,
        spreadsheet_source: Union[str, Path, SpreadsheetInterface],
        auth_credentials: Dict[str, Any] = None,
        read_only: Optional[bool] = None,
    ) -> Iterator[SpreadsheetInterface]:
        """Context manager for automatic spreadsheet resource management.

        This ensures proper cleanup of spreadsheet resources even if
        exceptions occur.

        Args:
            spreadsheet_source: Either a Google Sheets URL, Excel file path,
                or SpreadsheetInterface
            auth_credentials: Authentication credentials (required for
                Google Sheets)
            read_only: Whether to open in read-only mode (None = auto-detect)

        Yields:
            SpreadsheetInterface instance

        Raises:
            ValidationError: If unable to create spreadsheet interface
            Exception: Any exception from spreadsheet creation (for proper error handling)
        """
        spreadsheet = None
        try:
            spreadsheet = self._get_spreadsheet(
                spreadsheet_source, auth_credentials, read_only
            )
            yield spreadsheet
        finally:
            if spreadsheet:
                try:
                    spreadsheet.close()
                except Exception:
                    pass  # Ignore cleanup errors

    def _execute_validation(
        self,
        validation_logic: Callable[[SpreadsheetInterface, ValidationResult], None],
        spreadsheet_source: Union[str, Path, SpreadsheetInterface],
        auth_credentials: Dict[str, Any] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Enhanced template method for executing validation with centralized handling.

        This enhanced method provides:
        - ValidationResult initialization
        - Enhanced spreadsheet resource management with dynamic detection
        - Centralized authentication handling
        - Intelligent defaults based on source type
        - Comprehensive error handling and logging
        - Result formatting

        Args:
            validation_logic: Function that performs the actual validation
            spreadsheet_source: Source identifier (local Excel, Google Sheets URL,
                              Drive file URL/ID, or SpreadsheetInterface)
            auth_credentials: Authentication credentials (auto-determined if not provided)
            **kwargs: Additional validator-specific parameters

        Returns:
            Dict with validation results
        """
        result = ValidationResult()

        try:
            # Determine read_only mode based on validation mode
            # If mode is "fix", we need write access; if "flag", read-only is fine
            mode = kwargs.get("mode", "flag")
            read_only = mode != "fix"  # False for fix, True for flag

            # Use enhanced managed spreadsheet with dynamic detection
            with self._managed_spreadsheet(
                spreadsheet_source, auth_credentials, read_only=read_only
            ) as spreadsheet:
                # Log source type for debugging/monitoring
                try:
                    metadata = spreadsheet.get_metadata()
                    self.logger.debug(
                        f"Processing {metadata.spreadsheet_type} source: {metadata.title} "
                        f"({len(metadata.sheet_names)} sheets)"
                    )
                except Exception:
                    self.logger.debug(f"Processing spreadsheet source in {mode} mode")

                # Execute the actual validation logic
                validation_logic(spreadsheet, result, **kwargs)

        except ValidationError:
            # ValidationErrors are expected and should be re-raised as-is
            raise
        except Exception as e:
            # Log unexpected errors for debugging
            self.logger.exception(f"Unexpected error in {self.id} validator")
            result.add_error(f"Unexpected error: {str(e)}")
            if not result.automated_log:
                result.set_automated_log(f"Unexpected error: {str(e)}")

        # Ensure automated log is set
        self._set_default_log_if_empty(result)

        return result.to_dict()

    def _process_all_sheets(
        self,
        spreadsheet: SpreadsheetInterface,
        sheet_processor: Callable[[str, List[List[Any]], ValidationResult], None],
        result: ValidationResult,
    ) -> None:
        """Helper method to process all sheets in a spreadsheet.

        Args:
            spreadsheet: SpreadsheetInterface instance
            sheet_processor: Function to process each sheet
            result: ValidationResult to accumulate results
        """
        try:
            # Get spreadsheet metadata to get all sheet names
            metadata = spreadsheet.get_metadata()
            all_tabs = metadata.sheet_names

            # Process each tab
            for tab_name in all_tabs:
                try:
                    # Get data for this specific sheet
                    sheet_data = spreadsheet.get_sheet_data(tab_name)

                    if sheet_data and sheet_data.values:
                        sheet_processor(tab_name, sheet_data.values, result)
                except Exception as tab_error:
                    # Log the error but continue with other tabs
                    self.logger.warning(
                        f"Failed to process tab '{tab_name}': {str(tab_error)}"
                    )
                    continue
        except Exception as e:
            raise ValidationError(f"Failed to process spreadsheet sheets: {str(e)}")

    def _process_sheet_cells(
        self,
        sheet_data: List[List[Any]],
        cell_processor: Callable[[int, int, Any], Optional[Dict[str, Any]]],
        skip_empty: bool = True,
    ) -> List[Dict[str, Any]]:
        """Helper method to process individual cells in sheet data.

        Args:
            sheet_data: 2D list of cell values
            cell_processor: Function to process each cell, returns issue dict
                or None
            skip_empty: Whether to skip empty cells

        Returns:
            List of flags found
        """
        flags = []

        for row_idx, row in enumerate(sheet_data):
            for col_idx, cell in enumerate(row):
                if skip_empty and (
                    not cell or (isinstance(cell, str) and not cell.strip())
                ):
                    continue

                issue = cell_processor(row_idx, col_idx, cell)
                if issue:
                    flags.append(issue)
        return flags

    def _apply_fixes_to_sheet(
        self,
        spreadsheet: SpreadsheetInterface,
        sheet_name: str,
        original_data: List[List[Any]],
        fixes: List[Dict[str, Any]],
    ) -> None:
        """Helper method to apply fixes to a sheet.

        Args:
            spreadsheet: SpreadsheetInterface instance
            sheet_name: Name of the sheet to update
            original_data: Original sheet data
            fixes: List of fixes to apply (each with row, col, new_value)
        """
        if not fixes:
            return

        # Create a copy of the original data
        fixed_data = [row[:] for row in original_data]

        # Apply all fixes
        for fix in fixes:
            row_idx = fix.get("row", 0)
            col_idx = fix.get("col", 0)
            new_value = fix.get("new_value", "")

            if 0 <= row_idx < len(fixed_data) and 0 <= col_idx < len(
                fixed_data[row_idx]
            ):
                fixed_data[row_idx][col_idx] = new_value

        # Update the sheet
        self._update_sheet_data(spreadsheet, sheet_name, fixed_data)

    def _generate_cell_reference(
        self, row_idx: int, col_idx: int, sheet_name: str = None
    ) -> str:
        """Generate a cell reference in A1 notation.

        Args:
            row_idx: 0-based row index
            col_idx: 0-based column index
            sheet_name: Optional sheet name to include

        Returns:
            Cell reference (e.g., "A1" or "Sheet1!A1")
        """
        # Convert column index to letter
        col_letter = ""
        col_num = col_idx + 1
        while col_num > 0:
            col_num -= 1
            col_letter = chr(col_num % 26 + ord("A")) + col_letter
            col_num //= 26

        cell_ref = f"{col_letter}{row_idx + 1}"

        if sheet_name:
            # Escape sheet name if it contains special characters
            if any(char in sheet_name for char in [" ", "'", '"', "!", "#"]):
                sheet_name = f"'{sheet_name}'"
            cell_ref = f"{sheet_name}!{cell_ref}"
        return cell_ref

    def _create_sheets_service(self, auth_credentials: Dict[str, Any]) -> Any:
        """Create Google Sheets service from auth credentials.

        Args:
            auth_credentials: Authentication credentials dict

        Returns:
            Google Sheets service instance

        Raises:
            ValidationError: If unable to create sheets service
        """
        try:
            from urarovite.auth.google_sheets import (
                create_sheets_service_from_encoded_creds,
            )

            # Try different credential key names for compatibility
            encoded_creds = (
                auth_credentials.get("encoded_credentials")
                or auth_credentials.get("auth_secret")
                or auth_credentials.get("encoded_creds", "")
            )

            if not encoded_creds:
                raise ValidationError(
                    "No encoded credentials found in auth_credentials"
                )

            return create_sheets_service_from_encoded_creds(encoded_creds)

        except Exception as e:
            raise ValidationError(f"Failed to create sheets service: {str(e)}")

    def _extract_sheet_id_from_url(self, url: str) -> str:
        """Extract sheet ID from Google Sheets URL.

        Args:
            url: Google Sheets URL

        Returns:
            Sheet ID string

        Raises:
            ValidationError: If URL is invalid or sheet ID cannot be extracted
        """
        try:
            from urarovite.utils.sheets import extract_sheet_id

            if not url or not isinstance(url, str):
                raise ValidationError("Invalid or empty URL provided")

            if "docs.google.com" not in url:
                raise ValidationError("URL is not a Google Sheets URL")

            sheet_id = extract_sheet_id(url)
            if not sheet_id:
                raise ValidationError("Could not extract sheet ID from URL")

            return sheet_id

        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Failed to extract sheet ID: {str(e)}")

    def _set_default_log_if_empty(self, result: ValidationResult) -> None:
        """Set default automated log if none was set.

        Args:
            result: ValidationResult to update
        """
        if not result.automated_log:
            if result.flags_found > 0:
                result.set_automated_log(f"Found {result.flags_found} flags")
            elif result.fixes_applied > 0:
                result.set_automated_log(f"Applied {result.fixes_applied} fixes")
            else:
                result.set_automated_log("No flags found")

    def __str__(self) -> str:
        return f"{self.name} ({self.id})"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id='{self.id}', name='{self.name}')>"
