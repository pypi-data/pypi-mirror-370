"""Spreadsheet abstraction layer for supporting multiple spreadsheet formats.

This module provides a unified interface for working with different spreadsheet
formats (Google Sheets, Excel files, etc.) through a common abstraction layer.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Tuple
from pathlib import Path

from urarovite.core.exceptions import ValidationError


class SpreadsheetMetadata:
    """Metadata about a spreadsheet."""

    def __init__(
        self,
        spreadsheet_id: str,
        title: str,
        sheet_names: List[str],
        spreadsheet_type: str,
        url: Optional[str] = None,
        file_path: Optional[Path] = None,
    ) -> None:
        self.spreadsheet_id = spreadsheet_id
        self.title = title
        self.sheet_names = sheet_names
        self.spreadsheet_type = spreadsheet_type
        self.url = url
        self.file_path = file_path


class SheetData:
    """Container for sheet data and metadata."""

    def __init__(
        self, values: List[List[Any]], sheet_name: str, rows: int, cols: int
    ) -> None:
        self.values = values
        self.sheet_name = sheet_name
        self.rows = rows
        self.cols = cols


class SpreadsheetInterface(ABC):
    """Abstract interface for spreadsheet operations.

    This interface defines the common operations that all spreadsheet
    implementations must support, regardless of the underlying format
    (Google Sheets, Excel, etc.).
    """

    @abstractmethod
    def get_metadata(self) -> SpreadsheetMetadata:
        """Get spreadsheet metadata including sheet names.

        Returns:
            SpreadsheetMetadata object with spreadsheet information

        Raises:
            ValidationError: If unable to access spreadsheet metadata
        """
        pass

    @abstractmethod
    def get_sheet_data(
        self, sheet_name: Optional[str] = None, range_name: Optional[str] = None
    ) -> SheetData:
        """Get data from a specific sheet or range.

        Args:
            sheet_name: Name of the sheet to read (uses first sheet if None)
            range_name: A1 notation range (e.g., 'A1:Z100', optional)

        Returns:
            SheetData object containing the sheet data

        Raises:
            ValidationError: If unable to read sheet data
        """
        pass

    @abstractmethod
    def get_sheet_data_with_hyperlinks(
        self,
        sheet_name: Optional[str] = None,
        range_name: Optional[str] = None,
    ) -> SheetData:
        """
        Get data from a specific sheet, resolving hyperlinks to their URLs.

        Args:
            sheet_name: Name of the sheet to read (uses first sheet if None).
            range_name: A1 notation range (e.g., 'A1:Z100', optional).

        Returns:
            SheetData object containing the sheet data with hyperlinks as URLs.

        Raises:
            ValidationError: If unable to read sheet data.
        """
        # Default implementation falls back to get_sheet_data
        return self.get_sheet_data(sheet_name, range_name)

    @abstractmethod
    def update_sheet_data(
        self,
        sheet_name: str,
        values: List[List[Any]],
        start_row: int = 1,
        start_col: int = 1,
        range_name: Optional[str] = None,
    ) -> None:
        """Update data in a specific sheet.

        Args:
            sheet_name: Name of the sheet to update
            values: 2D list of values to write
            start_row: Starting row (1-based, default: 1)
            start_col: Starting column (1-based, default: 1)
            range_name: A1 notation range (optional, overrides start_row/start_col)

        Raises:
            ValidationError: If unable to update sheet data
        """
        pass

    def update_sheet_formulas(
        self, sheet_name: str, formulas: Dict[str, str], preserve_values: bool = True
    ) -> None:
        """Update formulas in a specific sheet.

        Args:
            sheet_name: Name of the sheet to update
            formulas: Dict mapping cell coordinates to formulas (e.g., {"A1": "=SUM(B1:B10)"})
            preserve_values: Whether to preserve existing values for non-formula cells

        Raises:
            ValidationError: If unable to update formulas
        """
        # Default implementation: convert formulas to values (fallback)
        # Subclasses should override for proper formula support
        if not formulas:
            return

        # Get current sheet data to preserve non-formula cells
        if preserve_values:
            self.get_sheet_data(sheet_name)
        else:
            # Create empty grid based on formula positions
            max_row = max_col = 0
            for cell_ref in formulas.keys():
                row, col = self._parse_cell_reference(cell_ref)
                max_row = max(max_row, row)
                max_col = max(max_col, col)

            [["" for _ in range(max_col)] for _ in range(max_row)]

        # For default implementation, we can't actually set formulas,
        # so we'll just warn and skip
        import logging

        logging.warning(
            f"Formula update not supported for {type(self).__name__}. "
            f"Formulas will be lost: {list(formulas.keys())}"
        )

    def get_sheet_data_with_formulas(
        self, sheet_name: Optional[str] = None, range_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get both values and formulas from a sheet.

        Args:
            sheet_name: Name of the sheet to read (uses first sheet if None)
            range_name: A1 notation range (e.g., 'A1:Z100', optional)

        Returns:
            Dict with keys:
            - values: 2D list of cell values
            - formulas: Dict mapping cell coordinates to formulas
            - sheet_name: Name of the sheet
            - rows: Number of rows with data
            - cols: Number of columns with data
        """
        # Get regular data
        sheet_data = self.get_sheet_data(sheet_name, range_name)

        # Get formulas for this sheet
        all_formulas = self.get_formulas(sheet_name)
        sheet_formulas = all_formulas.get(sheet_data.sheet_name, {})

        return {
            "values": sheet_data.values,
            "formulas": sheet_formulas,
            "sheet_name": sheet_data.sheet_name,
            "rows": sheet_data.rows,
            "cols": sheet_data.cols,
        }

    def _parse_cell_reference(self, cell_ref: str) -> Tuple[int, int]:
        """Parse cell reference like 'A1' into row/column indices.

        Args:
            cell_ref: Cell reference (e.g., 'A1', 'Z100')

        Returns:
            Tuple of (row, col) - both 1-based
        """
        import re

        match = re.match(r"^([A-Z]+)(\d+)$", cell_ref.upper())
        if not match:
            raise ValidationError(f"Invalid cell reference: {cell_ref}")

        col_letters, row_str = match.groups()

        # Convert column letters to index (A=1, B=2, ..., AA=27, etc.)
        col_idx = 0
        for i, char in enumerate(reversed(col_letters)):
            col_idx += (ord(char) - ord("A") + 1) * (26**i)

        row_idx = int(row_str)

        return row_idx, col_idx

    @abstractmethod
    def update_sheet_properties(
        self, sheet_name: str, new_name: Optional[str] = None, **properties: Any
    ) -> None:
        """Update sheet properties like name.

        Args:
            sheet_name: Current name of the sheet
            new_name: New name for the sheet (optional)
            **properties: Additional properties to update

        Raises:
            ValidationError: If unable to update sheet properties
        """
        pass

    @abstractmethod
    def create_sheet(self, sheet_name: str) -> None:
        """Create a new sheet.

        Args:
            sheet_name: Name of the new sheet

        Raises:
            ValidationError: If unable to create sheet
        """
        pass

    @abstractmethod
    def delete_sheet(self, sheet_name: str) -> None:
        """Delete a sheet.

        Args:
            sheet_name: Name of the sheet to delete

        Raises:
            ValidationError: If unable to delete sheet
        """
        pass

    @abstractmethod
    def save(self) -> None:
        """Save changes to the spreadsheet.

        For Google Sheets, this is typically a no-op since changes
        are saved automatically. For Excel files, this writes to disk.

        Raises:
            ValidationError: If unable to save spreadsheet
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the spreadsheet and clean up resources.

        Raises:
            ValidationError: If unable to close spreadsheet properly
        """
        pass

    def get_formulas(
        self, sheet_name: Optional[str] = None
    ) -> Dict[str, Dict[str, str]]:
        """Get formulas from spreadsheet sheets.

        Args:
            sheet_name: Name of specific sheet (optional, gets all sheets if None)

        Returns:
            Dict mapping sheet names to dict of cell coordinates to formulas
            Example: {"Sheet1": {"A1": "=SUM(B1:B10)", "B5": "=NOW()"}}

        Raises:
            ValidationError: If unable to read formulas
        """
        # Default implementation returns empty dict (no formulas)
        # Subclasses can override to provide formula reading capability
        return {}

    def get_sheet_formulas(self, sheet_name: str) -> Dict[str, str]:
        """Get formulas from a specific sheet.

        Args:
            sheet_name: Name of the sheet to get formulas from

        Returns:
            Dict mapping cell coordinates to formulas for the specified sheet
            Example: {"A1": "=SUM(B1:B10)", "B5": "=NOW()"}

        Raises:
            ValidationError: If unable to read formulas from the sheet
        """
        # Default implementation uses get_formulas and extracts the specific sheet
        all_formulas = self.get_formulas(sheet_name)
        return all_formulas.get(sheet_name, {})

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures cleanup."""
        self.close()

    def get_next_available_column(self, sheet_name: Optional[str] = None) -> str:
        """Get the next available column letter for writing data.

        Args:
            sheet_name: Name of sheet to check (uses first sheet if None)

        Returns:
            Column letter (e.g., 'A', 'B', 'AA')
        """
        sheet_data = self.get_sheet_data(sheet_name)
        next_col_num = sheet_data.cols + 1

        # Convert column number to letter (A=1, B=2, etc.)
        result = ""
        while next_col_num > 0:
            next_col_num -= 1
            result = chr(65 + next_col_num % 26) + result
            next_col_num //= 26
        return result


class SpreadsheetFactory:
    """Factory for creating spreadsheet instances based on input type."""

    @staticmethod
    def create_spreadsheet(
        source: Union[str, Path],
        auth_credentials: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> SpreadsheetInterface:
        """Create a spreadsheet instance based on the source type.

        Args:
            source: Either a Google Sheets URL or path to Excel file
            auth_credentials: Authentication credentials (for Google Sheets)
            **kwargs: Additional arguments for specific implementations
                     - create_new: For Excel files, create new file if it doesn't exist

        Returns:
            SpreadsheetInterface implementation

        Raises:
            ValidationError: If unable to determine or create spreadsheet type
        """
        from urarovite.core.spreadsheet_google import GoogleSheetsSpreadsheet
        from urarovite.core.spreadsheet_excel import ExcelSpreadsheet

        # Determine spreadsheet type based on source
        if isinstance(source, str) and (
            "docs.google.com" in source or "sheets.google.com" in source
        ):
            # Google Sheets URL
            if not auth_credentials:
                raise ValidationError(
                    "Authentication credentials required for Google Sheets"
                )
            # Filter kwargs to only include parameters that GoogleSheetsSpreadsheet accepts
            google_kwargs = {}
            if "subject" in kwargs:
                google_kwargs["subject"] = kwargs["subject"]
            return GoogleSheetsSpreadsheet(source, auth_credentials, **google_kwargs)

        elif isinstance(source, (str, Path)):
            # Assume Excel file
            file_path = Path(source)
            create_new = kwargs.get("create_new", False)

            # PERFORMANCE OPTIMIZATION: Default to read_only=True if not specified
            # This dramatically improves Excel reading performance
            if "read_only" not in kwargs and not create_new:
                kwargs["read_only"] = True

            # If not creating new, check file existence and extension
            if not create_new:
                if not file_path.exists():
                    raise ValidationError(f"Excel file not found: {file_path}")

                # Check file extension for existing files
                if file_path.suffix.lower() not in [".xlsx", ".xls", ".xlsm"]:
                    raise ValidationError(
                        f"Unsupported file format: {file_path.suffix}"
                    )
            else:
                # For new files, ensure .xlsx extension
                if file_path.suffix.lower() not in [".xlsx", ".xls", ".xlsm"]:
                    file_path = file_path.with_suffix(".xlsx")
                    # Update the source in kwargs for ExcelSpreadsheet
                    kwargs["file_path"] = file_path

            return ExcelSpreadsheet(file_path, **kwargs)

        else:
            raise ValidationError(f"Unsupported source type: {type(source)}")
