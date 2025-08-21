"""Generic spreadsheet utilities for format-agnostic operations.

This module provides utilities that work with any spreadsheet format
through the unified SpreadsheetInterface abstraction.
"""

import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from urarovite.core.spreadsheet import SpreadsheetFactory
from urarovite.core.exceptions import ValidationError
from urarovite.utils.drive import detect_spreadsheet_type


def get_spreadsheet_tabs(
    spreadsheet_source: Union[str, Path],
    auth_credentials: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Get tab names from any spreadsheet source.

    Args:
        spreadsheet_source: Google Sheets URL or Excel file path
        auth_credentials: Authentication credentials (required for Google Sheets)

    Returns:
        Dict with keys: accessible, tabs, error
    """
    try:
        with SpreadsheetFactory.create_spreadsheet(
            spreadsheet_source, auth_credentials
        ) as spreadsheet:
            metadata = spreadsheet.get_metadata()
            return {"accessible": True, "tabs": metadata.sheet_names, "error": None}
    except Exception as e:
        return {"accessible": False, "tabs": [], "error": str(e)}


def get_spreadsheet_data(
    spreadsheet_source: Union[str, Path],
    range_name: str,
    auth_credentials: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Get data from any spreadsheet source.

    Args:
        spreadsheet_source: Google Sheets URL or Excel file path
        range_name: A1 notation range (e.g., 'Sheet1!A1:Z100')
        auth_credentials: Authentication credentials (required for Google Sheets)

    Returns:
        Dict with keys: success, values, rows, cols, error
    """
    try:
        with SpreadsheetFactory.create_spreadsheet(
            spreadsheet_source, auth_credentials
        ) as spreadsheet:
            # Parse range to get sheet name
            if "!" in range_name:
                sheet_name, cell_range = range_name.split("!", 1)
                sheet_name = sheet_name.strip("'")
            else:
                sheet_name = None
                cell_range = range_name

            sheet_data = spreadsheet.get_sheet_data(sheet_name, cell_range)
            return {
                "success": True,
                "values": sheet_data.values,
                "rows": sheet_data.rows,
                "cols": sheet_data.cols,
                "error": None,
            }
    except Exception as e:
        return {"success": False, "values": [], "rows": 0, "cols": 0, "error": str(e)}


def update_spreadsheet_data(
    spreadsheet_source: Union[str, Path],
    sheet_name: str,
    values: List[List[Any]],
    range_name: str,
    auth_credentials: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Update data in any spreadsheet source.

    Args:
        spreadsheet_source: Google Sheets URL or Excel file path
        sheet_name: Name of the sheet to update
        values: 2D list of values to write
        range_name: A1 notation range (e.g., 'A1:Z100')
        auth_credentials: Authentication credentials (required for Google Sheets)

    Returns:
        Dict with keys: success, error
    """
    try:
        with SpreadsheetFactory.create_spreadsheet(
            spreadsheet_source, auth_credentials
        ) as spreadsheet:
            # Parse range to get start row and column
            if ":" in range_name:
                start_cell, end_cell = range_name.split(":", 1)
                start_row, start_col = _parse_cell_reference(start_cell)
            else:
                start_row, start_col = _parse_cell_reference(range_name)

            # Update the sheet data
            spreadsheet.update_sheet_data(
                sheet_name, values, start_row=start_row, start_col=start_col
            )
            spreadsheet.save()

            return {"success": True, "error": None}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_spreadsheet_formulas(
    spreadsheet_source: Union[str, Path],
    sheet_name: Optional[str] = None,
    auth_credentials: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Get formulas from any spreadsheet source.

    Args:
        spreadsheet_source: Google Sheets URL or Excel file path
        sheet_name: Optional specific sheet name to check
        auth_credentials: Authentication credentials (required for Google Sheets)

    Returns:
        Dict with keys: success, formulas, error
    """
    try:
        with SpreadsheetFactory.create_spreadsheet(
            spreadsheet_source, auth_credentials
        ) as spreadsheet:
            if sheet_name:
                sheet_data = spreadsheet.get_sheet_data(sheet_name)
                formulas = []
                for row_idx, row in enumerate(sheet_data.values):
                    for col_idx, cell in enumerate(row):
                        if isinstance(cell, str) and cell.startswith("="):
                            cell_ref = f"{chr(65 + col_idx)}{row_idx + 1}"
                            formulas.append({
                                "cell": cell_ref,
                                "formula": cell,
                                "sheet": sheet_name
                            })
            else:
                formulas = []
                for sheet_name in spreadsheet.get_metadata().sheet_names:
                    sheet_data = spreadsheet.get_sheet_data(sheet_name)
                    for row_idx, row in enumerate(sheet_data.values):
                        for col_idx, cell in enumerate(row):
                            if isinstance(cell, str) and cell.startswith("="):
                                cell_ref = f"{chr(65 + col_idx)}{row_idx + 1}"
                                formulas.append({
                                    "cell": cell_ref,
                                    "formula": cell,
                                    "sheet": sheet_name
                                })
            
            return {"success": True, "formulas": formulas, "error": None}
    except Exception as e:
        return {"success": False, "formulas": [], "error": str(e)}


def rename_spreadsheet_sheet(
    spreadsheet_source: Union[str, Path],
    old_sheet_name: str,
    new_sheet_name: str,
    auth_credentials: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Rename a sheet in any spreadsheet source.

    Args:
        spreadsheet_source: Google Sheets URL or Excel file path
        old_sheet_name: Current name of the sheet
        new_sheet_name: New name for the sheet
        auth_credentials: Authentication credentials (required for Google Sheets)

    Returns:
        Dict with keys: success, error
    """
    try:
        with SpreadsheetFactory.create_spreadsheet(
            spreadsheet_source, auth_credentials
        ) as spreadsheet:
            # This would need to be implemented in the specific spreadsheet classes
            # For now, return an error indicating it's not implemented
            return {
                "success": False,
                "error": "Sheet renaming not yet implemented for this spreadsheet type"
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


def read_csv_data_from_spreadsheet(
    spreadsheet_source: Union[str, Path],
    sheet_name: str,
    auth_credentials: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Read CSV data from any spreadsheet source.

    Args:
        spreadsheet_source: Google Sheets URL or Excel file path
        sheet_name: Name of the sheet to read
        auth_credentials: Authentication credentials (required for Google Sheets)

    Returns:
        Dict with keys: success, data, error
    """
    try:
        with SpreadsheetFactory.create_spreadsheet(
            spreadsheet_source, auth_credentials
        ) as spreadsheet:
            sheet_data = spreadsheet.get_sheet_data(sheet_name)
            return {
                "success": True,
                "data": sheet_data.values,
                "error": None
            }
    except Exception as e:
        return {"success": False, "data": [], "error": str(e)}


def write_json_to_spreadsheet(
    spreadsheet_source: Union[str, Path],
    sheet_name: str,
    data: List[Dict[str, Any]],
    auth_credentials: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Write JSON data to any spreadsheet source.

    Args:
        spreadsheet_source: Google Sheets URL or Excel file path
        sheet_name: Name of the sheet to write to
        auth_credentials: Authentication credentials (required for Google Sheets)

    Returns:
        Dict with keys: success, error
    """
    try:
        with SpreadsheetFactory.create_spreadsheet(
            spreadsheet_source, auth_credentials
        ) as spreadsheet:
            # Convert JSON data to 2D list
            if not data:
                values = []
            else:
                # Get headers from first row
                headers = list(data[0].keys())
                values = [headers]
                
                # Add data rows
                for row_data in data:
                    row_values = [row_data.get(header, "") for header in headers]
                    values.append(row_values)
            
            # Update the sheet
            spreadsheet.update_sheet_data(sheet_name, values)
            spreadsheet.save()
            
            return {"success": True, "error": None}
    except Exception as e:
        return {"success": False, "error": str(e)}


def convert_google_sheets_to_excel(
    google_sheets_url: str,
    excel_file_path: Union[str, Path],
    auth_credentials: Optional[Dict[str, Any]] = None,
    sheet_names: Optional[List[str]] = None,
    preserve_formulas: bool = True,
    preserve_visual_formatting: bool = True,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Convert Google Sheets to Excel format.

    Args:
        google_sheets_url: URL of the Google Sheets document
        excel_file_path: Path where the Excel file should be saved
        auth_credentials: Authentication credentials for Google Sheets
        sheet_names: Optional list of specific sheet names to convert
        preserve_formulas: Whether to preserve formulas and references
        preserve_visual_formatting: Whether to preserve fonts, colors, borders, etc.
        **kwargs: Additional arguments passed to the conversion function

    Returns:
        Dict with conversion results
    """
    try:
        excel_path = Path(excel_file_path)
        
        # Get original sheet name for auto-naming
        if excel_file_path == "auto" or excel_path.name == "auto":
            # Get the Google Sheets title for naming
            with SpreadsheetFactory.create_spreadsheet(
                google_sheets_url, auth_credentials
            ) as temp_spreadsheet:
                temp_metadata = temp_spreadsheet.get_metadata()
                original_name = temp_metadata.title
                # Clean the name for filesystem use (preserve more valid characters)
                # Allow: letters, numbers, spaces, hyphens, underscores, periods, parentheses, square brackets
                clean_name = "".join(
                    c
                    for c in original_name
                    if c.isalnum() or c in (" ", "-", "_", ".", "(", ")", "[", "]")
                ).rstrip()
                excel_path = excel_path.parent / f"{clean_name}.xlsx"

        # Ensure the directory exists
        excel_path.parent.mkdir(parents=True, exist_ok=True)

        # Ensure .xlsx extension
        if excel_path.suffix.lower() not in [".xlsx", ".xls", ".xlsm"]:
            excel_path = excel_path.with_suffix(".xlsx")
        
        # Ensure target directory exists
        excel_path.parent.mkdir(parents=True, exist_ok=True)

        # Use the SpreadsheetFactory to perform the conversion
        with SpreadsheetFactory.create_spreadsheet(
            google_sheets_url, auth_credentials
        ) as source_spreadsheet:
            source_metadata = source_spreadsheet.get_metadata()
            sheets_to_convert = sheet_names or source_metadata.sheet_names
            
            # Create target Excel file
            with SpreadsheetFactory.create_spreadsheet(
                excel_path, None, create_new=True
            ) as target_spreadsheet:
                converted_sheets = []
                errors = []
                
                for sheet_name in sheets_to_convert:
                    if sheet_name in source_metadata.sheet_names:
                        try:
                            # Get data from source
                            sheet_data = source_spreadsheet.get_sheet_data(sheet_name)
                            
                            # Update target
                            target_spreadsheet.update_sheet_data(sheet_name, sheet_data.values)
                            converted_sheets.append(sheet_name)
                        except Exception as e:
                            # Log individual sheet errors but continue with other sheets
                            import logging
                            logging.warning(f"Failed to convert sheet '{sheet_name}': {e}")
                            errors.append(f"Sheet '{sheet_name}': {str(e)}")
                
                # Remove unused initial sheets
                sheets_to_remove = []
                for sheet_name in target_spreadsheet.get_metadata().sheet_names:
                    if sheet_name not in converted_sheets:
                        sheets_to_remove.append(sheet_name)

                # Remove unused initial sheets
                for sheet_name in sheets_to_remove:
                    try:
                        target_spreadsheet.delete_sheet(sheet_name)
                        import logging
                        logging.info(f"Removed unused initial sheet: {sheet_name}")
                    except Exception as e:
                        import logging
                        logging.warning(f"Could not remove unused sheets: {e}")

                # Save the Excel file
                target_spreadsheet.save()

        # Return success if at least one sheet was converted
        success = len(converted_sheets) > 0
        return {
            "success": success,
            "converted_sheets": converted_sheets,
            "output_path": str(excel_path),
            "error": None if success else "; ".join(errors),
            "original_sheet_names": sheets_to_convert,
            "excel_sheet_names": converted_sheets,
        }

    except Exception as e:
        return {
            "success": False,
            "converted_sheets": [],
            "output_path": None,
            "error": str(e),
        }


def convert_excel_to_google_sheets(
    excel_file_path: Union[str, Path],
    google_sheets_url: str,
    auth_credentials: Dict[str, Any],
    sheet_names: Optional[List[str]] = None,
    create_new_sheets: bool = True,
    drive_folder_id: str | None = None,
) -> Dict[str, Any]:
    """Convert Excel file to Google Sheets using BULK operations.

    Note: If google_sheets_url is "auto", a new Google Sheet will be created
    using the Excel filename as the title.

    Args:
        excel_file_path: Path to the Excel file
        google_sheets_url: URL of the target Google Sheets document
        auth_credentials: Authentication credentials for Google Sheets
        sheet_names: Optional list of specific sheets to convert
                    (converts all if None)
        create_new_sheets: Whether to create new sheets if they don't exist
        drive_folder_id: Optional Google Drive folder ID for creating new Google Sheets

    Returns:
        Dict with keys: success, converted_sheets, error
    """
    try:
        excel_path = Path(excel_file_path)

        if not excel_path.exists():
            raise ValidationError(f"Excel file not found: {excel_path}")

        # Use the new bulk conversion function
        return convert_excel_to_google_sheets_bulk(
            excel_file_path=excel_path,
            google_sheets_url=google_sheets_url,
            auth_credentials=auth_credentials,
            sheet_names=sheet_names,
            create_new_sheets=create_new_sheets,
            drive_folder_id=drive_folder_id,
        )

    except Exception as e:
        return {"success": False, "converted_sheets": [], "error": str(e)}


def convert_excel_to_google_sheets_bulk(
    excel_file_path: Union[str, Path],
    google_sheets_url: str,
    auth_credentials: Dict[str, Any],
    sheet_names: Optional[List[str]] = None,
    create_new_sheets: bool = True,
    drive_folder_id: str | None = None,
) -> Dict[str, Any]:
    """Convert Excel to Google Sheets using SINGLE BULK API CALL.

    This function reads all Excel data first, then makes ONE batch update
    to Google Sheets instead of multiple individual sheet updates.

    Args:
        excel_file_path: Path to the Excel file
        google_sheets_url: URL of the target Google Sheets document
        auth_credentials: Authentication credentials for Google Sheets
        sheet_names: Optional list of specific sheets to convert
        create_new_sheets: Whether to create new sheets if they don't exist
        drive_folder_id: Optional Google Drive folder ID for creating new Google Sheets

    Returns:
        Dict with keys: success, converted_sheets, error
    """
    try:
        from urarovite.utils.sheets import extract_sheet_id, create_new_spreadsheet_in_folder
        from urarovite.auth.google_sheets import (
            create_sheets_service_from_encoded_creds,
        )

        excel_path = Path(excel_file_path)
        
        # Handle "auto" case - create new Google Sheet
        if google_sheets_url == "auto":
            # Extract auth credentials
            if isinstance(auth_credentials, dict):
                encoded_creds = auth_credentials.get("auth_secret")
                if not encoded_creds:
                    raise ValidationError("No auth_secret found in auth_credentials")
            else:
                encoded_creds = auth_credentials
            
            # Create gspread client for new sheet creation
            import gspread
            from urarovite.auth.google_sheets import decode_service_account
            
            service_account_info = decode_service_account(encoded_creds)
            gspread_client = gspread.service_account_from_dict(service_account_info)
            
            # Create new spreadsheet with Excel filename as title
            spreadsheet_name = excel_path.stem
            
            if drive_folder_id:
                # Create in specified folder
                new_spreadsheet = create_new_spreadsheet_in_folder(
                    gspread_client, drive_folder_id, spreadsheet_name
                )
                if not new_spreadsheet:
                    raise ValidationError(f"Failed to create spreadsheet in folder {drive_folder_id}")
            else:
                # Service accounts can't create sheets in their own drive without proper permissions
                raise ValidationError(
                    "For Excel to Google Sheets conversion, please specify a --drive-folder-id "
                    "where the service account has write access. Service accounts cannot "
                    "create sheets in their own drive without proper Drive API setup."
                )
            
            google_sheets_url = new_spreadsheet.url
            spreadsheet_id = new_spreadsheet.id
        else:
            spreadsheet_id = extract_sheet_id(google_sheets_url)
            if not spreadsheet_id:
                raise ValidationError(f"Invalid Google Sheets URL: {google_sheets_url}")

        # Extract auth credentials (if not already done for auto case)
        if google_sheets_url != "auto":
            if isinstance(auth_credentials, dict):
                encoded_creds = auth_credentials.get("auth_secret")
                if not encoded_creds:
                    raise ValidationError("No auth_secret found in auth_credentials")
            else:
                encoded_creds = auth_credentials

        # Create Google Sheets service
        sheets_service = create_sheets_service_from_encoded_creds(encoded_creds)

        converted_sheets = []

        # Step 1: Read ALL Excel data into memory
        excel_data = {}
        with SpreadsheetFactory.create_spreadsheet(
            excel_path, read_only=True
        ) as source_spreadsheet:
            source_metadata = source_spreadsheet.get_metadata()

            # Determine which sheets to convert
            sheets_to_convert = (
                sheet_names if sheet_names else source_metadata.sheet_names
            )

            # Read all sheet data
            for sheet_name in sheets_to_convert:
                try:
                    sheet_data = source_spreadsheet.get_sheet_data(sheet_name)
                    if sheet_data.values:
                        excel_data[sheet_name] = sheet_data.values
                        converted_sheets.append(sheet_name)
                except Exception as e:
                    import logging

                    logging.warning(f"Failed to read sheet '{sheet_name}': {e}")

        if not excel_data:
            return {
                "success": True,
                "converted_sheets": [],
                "error": "No data to convert",
            }

        # Step 2: Get current Google Sheets metadata
        with SpreadsheetFactory.create_spreadsheet(
            google_sheets_url, auth_credentials
        ) as target_spreadsheet:
            target_metadata = target_spreadsheet.get_metadata()
            existing_sheets = set(target_metadata.sheet_names)

            # Create missing sheets if needed
            for sheet_name in excel_data.keys():
                if sheet_name not in existing_sheets and create_new_sheets:
                    target_spreadsheet.create_sheet(sheet_name)

        # Step 3: Prepare BULK batch update request
        batch_requests = []

        for sheet_name, values in excel_data.items():
            # Prepare range for this sheet
            end_row = len(values)
            end_col_letter = _get_column_letter(len(values[0]) if values else 1)
            range_name = f"'{sheet_name}'!A1:{end_col_letter}{end_row}"

            # Add to batch request
            batch_requests.append({"range": range_name, "values": values})

        # Step 4: Execute SINGLE BULK UPDATE
        if batch_requests:
            batch_body = {"valueInputOption": "RAW", "data": batch_requests}

            result = (
                sheets_service.spreadsheets()
                .values()
                .batchUpdate(spreadsheetId=spreadsheet_id, body=batch_body)
                .execute()
            )

            total_updated_cells = sum(
                response.get("updatedCells", 0)
                for response in result.get("responses", [])
            )

            import logging

            logging.info(
                f"Bulk update completed: {total_updated_cells} cells updated in single API call"
            )

        # Step 5: Remove default sheets that weren't converted from source
        if converted_sheets:
            try:
                with SpreadsheetFactory.create_spreadsheet(
                    google_sheets_url, auth_credentials, read_only=False
                ) as target_spreadsheet:
                    final_metadata = target_spreadsheet.get_metadata()
                    for default_name in ["Sheet", "Sheet1"]:
                        if (
                            default_name in final_metadata.sheet_names
                            and default_name not in converted_sheets
                            and len(final_metadata.sheet_names) > 1
                        ):
                            target_spreadsheet.delete_sheet(default_name)
                            import logging

                            logging.info(
                                f"Removed unused default sheet: {default_name}"
                            )
            except Exception as e:
                import logging

                logging.warning(f"Could not remove default sheet: {e}")

        result = {"success": True, "converted_sheets": converted_sheets, "error": None}
        
        # Include the Google Sheets URL (especially important for auto-created sheets)
        result["output_url"] = google_sheets_url
        
        return result

    except Exception as e:
        return {"success": False, "converted_sheets": [], "error": str(e)}


def _get_column_letter(col_num: int) -> str:
    """Convert column number to Excel column letter (1=A, 2=B, etc.)."""
    result = ""
    while col_num > 0:
        col_num -= 1
        result = chr(col_num % 26 + ord("A")) + result
        col_num //= 26
    return result


def _resolve_target_name(
    source: Union[str, Path],
    target: Union[str, Path],
    auth_credentials: Optional[Dict[str, Any]] = None,
    use_temp_directory: bool = True,
) -> Union[str, Path]:
    """Resolve target name using original source name if target is 'auto'.

    Args:
        source: Source spreadsheet (Google Sheets URL or Excel file path)
        target: Target path or 'auto' for automatic naming
        auth_credentials: Auth credentials for Google Sheets access
        use_temp_directory: If True, place Excel files in temp/ directory (for temporary processing)
                           If False, place Excel files in output/ directory (for final output)

    Returns:
        Resolved target path/URL with proper naming
    """
    if str(target) != "auto":
        return target

    try:
        # Get source metadata to extract original name
        with SpreadsheetFactory.create_spreadsheet(
            source, auth_credentials
        ) as source_spreadsheet:
            metadata = source_spreadsheet.get_metadata()
            original_name = metadata.title

            # Clean the name for filesystem use (preserve more valid characters)
            # Allow: letters, numbers, spaces, hyphens, underscores, periods, parentheses, square brackets
            clean_name = "".join(
                c
                for c in original_name
                if c.isalnum() or c in (" ", "-", "_", ".", "(", ")", "[", "]")
            ).rstrip()
            if not clean_name:
                clean_name = "Converted_Spreadsheet"

            # Determine target format based on source
            source_is_google = isinstance(source, str) and (
                "docs.google.com" in source or "sheets.google.com" in source
            )

            if source_is_google:
                # Google Sheets → Excel: return filename with .xlsx extension
                directory = "temp" if use_temp_directory else "output"
                target_path = Path(directory) / f"{clean_name}.xlsx"
                # Generate unique filename if it already exists
                return _generate_unique_filename(target_path)
            else:
                # Excel → Google Sheets: return clean name (will be created as new sheet)
                return clean_name

    except Exception:
        # Fallback naming if metadata extraction fails
        if isinstance(source, (str, Path)) and not (
            "docs.google.com" in str(source) or "sheets.google.com" in str(source)
        ):
            # Excel source
            source_path = Path(source)
            return source_path.stem  # Return filename without extension
        else:
            # Google Sheets source - use appropriate directory
            directory = "temp" if use_temp_directory else "output"
            target_path = Path(directory) / "Converted_Spreadsheet.xlsx"
            # Generate unique filename if it already exists
            return _generate_unique_filename(target_path)


def convert_spreadsheet_format(
    source: Union[str, Path],
    target: Union[str, Path],
    auth_credentials: Optional[Dict[str, Any]] = None,
    sheet_names: Optional[List[str]] = None,
    preserve_formulas: bool = True,  # DEFAULT: Always preserve formulas
    preserve_visual_formatting: bool = True,  # DEFAULT: Always preserve visual formatting
    source_file_type: Optional[str] = None,  # Override automatic type detection
    target_file_type: Optional[str] = None,  # Override automatic type detection
    use_temp_directory: bool = True,  # Place auto-generated files in temp/ vs output/
    **kwargs: Any,
) -> Dict[str, Any]:
    """Convert between spreadsheet formats automatically.

    Detects source and target formats and performs appropriate conversion.
    Can preserve formulas, cell references, and visual formatting during conversion.

    Args:
        source: Source spreadsheet (Google Sheets URL or Excel file path)
        target: Target spreadsheet (Google Sheets URL or Excel file path)
        auth_credentials: Authentication credentials (required for Google Sheets)
        sheet_names: Optional list of specific sheets to convert
        preserve_formulas: Whether to preserve formulas and references (default: True - RECOMMENDED)
        preserve_visual_formatting: Whether to preserve fonts, colors, borders, etc. (default: True - RECOMMENDED)
        use_temp_directory: If True, place auto-generated files in temp/ directory (default)
                           If False, place auto-generated files in output/ directory
        **kwargs: Additional arguments passed to specific conversion functions

    Returns:
        Dict with keys: success, conversion_type, converted_sheets,
                       formula_stats (if preserve_formulas=True),
                       formatting_stats (if preserve_visual_formatting=True), error
    """
    try:
        # Resolve target name if 'auto' is specified
        target = _resolve_target_name(
            source, target, auth_credentials, use_temp_directory
        )

        # Ensure temp directory exists if target path uses temp
        if isinstance(target, Path) and "temp" in target.parts:
            target.parent.mkdir(parents=True, exist_ok=True)

        # Use enhanced formatting conversion if requested
        if preserve_visual_formatting:
            try:
                from urarovite.utils.enhanced_conversion import (
                    convert_with_full_formatting,
                )

                return convert_with_full_formatting(
                    source=source,
                    target=target,
                    auth_credentials=auth_credentials,
                    sheet_names=sheet_names,
                    preserve_formulas=preserve_formulas,
                    preserve_visual_formatting=True,
                    source_file_type=source_file_type,
                    target_file_type=target_file_type,
                )
            except ImportError:
                import logging

                logging.warning(
                    "Enhanced formatting not available - falling back to basic conversion"
                )

        # Use formula-aware conversion if requested
        if preserve_formulas:
            from urarovite.utils.formula_aware_conversion import convert_with_formulas

            result = convert_with_formulas(
                source=source,
                target=target,
                auth_credentials=auth_credentials,
                sheet_names=sheet_names,
                translate_references=True,
                source_file_type=source_file_type,
                target_file_type=target_file_type,
            )

            # Determine conversion type for consistency (with override support)
            if source_file_type:
                # Use explicit override
                source_is_google = source_file_type.lower() in [
                    "google_sheets",
                    "sheets",
                    "google",
                ]
            else:
                # Use URL-based detection
                source_is_google = isinstance(source, str) and (
                    "docs.google.com" in source or "sheets.google.com" in source
                )

            if target_file_type:
                # Use explicit override
                target_is_google = target_file_type.lower() in [
                    "google_sheets",
                    "sheets",
                    "google",
                ]
            else:
                # Use URL-based detection
                target_is_google = isinstance(target, str) and (
                    "docs.google.com" in target or "sheets.google.com" in target
                )

            if source_is_google and not target_is_google:
                conversion_type = "google_sheets_to_excel"
            elif not source_is_google and target_is_google:
                conversion_type = "excel_to_google_sheets"
            elif source_is_google and target_is_google:
                conversion_type = "google_sheets_to_google_sheets"
            elif not source_is_google and not target_is_google:
                conversion_type = "excel_to_excel"
            else:
                conversion_type = "unknown"

            result["conversion_type"] = conversion_type
            return result

        # Fall back to values-only conversion
        # Detect source and target types (with override support)
        if source_file_type:
            # Use explicit override
            source_is_google = source_file_type.lower() in [
                "google_sheets",
                "sheets",
                "google",
            ]
        else:
            # Use URL-based detection
            source_is_google = isinstance(source, str) and (
                "docs.google.com" in source or "sheets.google.com" in source
            )

        if target_file_type:
            # Use explicit override
            target_is_google = target_file_type.lower() in [
                "google_sheets",
                "sheets",
                "google",
            ]
        else:
            # Use URL-based detection
            target_is_google = isinstance(target, str) and (
                "docs.google.com" in target or "sheets.google.com" in target
            )

        if source_is_google and not target_is_google:
            # Google Sheets to Excel
            result = convert_google_sheets_to_excel(
                source, target, auth_credentials, sheet_names, **kwargs
            )
            result["conversion_type"] = "google_sheets_to_excel"

        elif not source_is_google and target_is_google:
            # Excel to Google Sheets
            result = convert_excel_to_google_sheets(
                source, target, auth_credentials, sheet_names, **kwargs
            )
            result["conversion_type"] = "excel_to_google_sheets"

        elif source_is_google and target_is_google:
            # Google Sheets to Google Sheets (copy)
            result = _copy_google_sheets_to_google_sheets(
                source, target, auth_credentials, sheet_names, **kwargs
            )
            result["conversion_type"] = "google_sheets_to_google_sheets"

        elif not source_is_google and not target_is_google:
            # Excel to Excel (copy)
            result = _copy_excel_to_excel(source, target, sheet_names, **kwargs)
            result["conversion_type"] = "excel_to_excel"

        else:
            raise ValidationError("Unable to determine conversion type")

        return result

    except Exception as e:
        return {
            "success": False,
            "conversion_type": "unknown",
            "converted_sheets": [],
            "error": str(e),
        }


def _copy_google_sheets_to_google_sheets(
    source_url: str,
    target_url: str,
    auth_credentials: Optional[Dict[str, Any]] = None,
    sheet_names: Optional[List[str]] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Copy data from one Google Sheets to another.

    Args:
        source_url: Source Google Sheets URL
        target_url: Target Google Sheets URL
        auth_credentials: Authentication credentials
        sheet_names: Optional list of specific sheet names to copy
        **kwargs: Additional arguments

    Returns:
        Dict with conversion results
    """
    try:
        # This is essentially a data copy operation between Google Sheets
        with SpreadsheetFactory.create_spreadsheet(
            source_url, auth_credentials
        ) as source_spreadsheet:
            source_metadata = source_spreadsheet.get_metadata()
            sheets_to_copy = sheet_names or source_metadata.sheet_names

            with SpreadsheetFactory.create_spreadsheet(
                target_url, auth_credentials
            ) as target_spreadsheet:
                copied_sheets = []
                
                for sheet_name in sheets_to_copy:
                    if sheet_name in source_metadata.sheet_names:
                        # Get data from source
                        sheet_data = source_spreadsheet.get_sheet_data(sheet_name)

                        # Update target
                        target_spreadsheet.update_sheet_data(sheet_name, sheet_data.values)
                        copied_sheets.append(sheet_name)
                
                target_spreadsheet.save()
                
                return {
                    "success": True,
                    "conversion_type": "google_sheets_to_google_sheets",
                    "converted_sheets": copied_sheets,
                    "error": None,
                }
    except Exception as e:
        return {
            "success": False,
            "conversion_type": "google_sheets_to_google_sheets",
            "converted_sheets": [],
            "error": str(e),
        }


def _copy_excel_to_excel(
    source_path: Union[str, Path],
    target_path: Union[str, Path],
    sheet_names: Optional[List[str]] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Copy data from one Excel file to another.

    Args:
        source_path: Source Excel file path
        target_path: Target Excel file path
        sheet_names: Optional list of specific sheet names to copy
        **kwargs: Additional arguments

    Returns:
        Dict with conversion results
    """
    try:
        source_path = Path(source_path)
        target_path = Path(target_path)
        
        # Ensure target directory exists
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Ensure .xlsx extension for target
        if target_path.suffix.lower() not in [".xlsx", ".xls", ".xlsm"]:
            target_path = target_path.with_suffix(".xlsx")
        
        # This is essentially a data copy operation between Excel files
        with SpreadsheetFactory.create_spreadsheet(source_path, None) as source_spreadsheet:
            source_metadata = source_spreadsheet.get_metadata()
            sheets_to_copy = sheet_names or source_metadata.sheet_names
            
            with SpreadsheetFactory.create_spreadsheet(target_path, None) as target_spreadsheet:
                copied_sheets = []
                
                for sheet_name in sheets_to_copy:
                    if sheet_name in source_metadata.sheet_names:
                        # Get data from source
                        sheet_data = source_spreadsheet.get_sheet_data(sheet_name)
                        
                        # Update target
                        target_spreadsheet.update_sheet_data(sheet_name, sheet_data.values)
                        copied_sheets.append(sheet_name)

                target_spreadsheet.save()

        return {
            "success": True,
            "conversion_type": "excel_to_excel",
            "converted_sheets": copied_sheets,
            "output_path": str(target_path),
            "error": None,
        }
    except Exception as e:
        return {
            "success": False,
            "conversion_type": "excel_to_excel",
            "converted_sheets": [],
            "error": str(e),
        }


def _generate_unique_filename(file_path: Path) -> Path:
    """Generate a unique filename by adding (1), (2), etc. if the file already exists.
    
    Args:
        file_path: The original file path
        
    Returns:
        A unique file path that doesn't exist
    """
    # Extract stem and extension
    stem = file_path.stem
    suffix = file_path.suffix
    parent = file_path.parent
    
    # Check if any files with similar names already exist
    # Look for files that start with the same stem and have optional (n) suffix
    existing_files = []
    for existing_file in parent.glob(f"{stem}*{suffix}"):
        if existing_file != file_path:  # Don't include the target file itself
            existing_files.append(existing_file)
    
    # Also check for files that match the exact stem pattern
    exact_matches = []
    for existing_file in existing_files:
        existing_stem = existing_file.stem
        # Check if this is the base name or a numbered version
        if existing_stem == stem:
            exact_matches.append(existing_file)
        elif re.match(rf'^{re.escape(stem)}\s*\(\d+\)\s*$', existing_stem):
            exact_matches.append(existing_file)
    
    # If no exact matches found with glob, try a more comprehensive search
    if not exact_matches:
        # Look for any files that might be related to this stem
        for existing_file in parent.iterdir():
            if existing_file.is_file() and existing_file.suffix == suffix:
                existing_stem = existing_file.stem
                # Check if this is the base name or a numbered version
                if existing_stem == stem:
                    exact_matches.append(existing_file)
                elif re.match(rf'^{re.escape(stem)}\s*\(\d+\)\s*$', existing_stem):
                    exact_matches.append(existing_file)
    
    if not exact_matches:
        # No similar files exist, return the original path
        return file_path
    
    # Check if stem already ends with (n)
    # Use a more robust regex that handles spaces and parentheses correctly
    match = re.match(r'^(.+?)\s*\((\d+)\)\s*$', stem)
    if match:
        base_stem = match.group(1).rstrip()  # Remove trailing spaces
        current_num = int(match.group(2))
        next_num = current_num + 1
    else:
        base_stem = stem
        next_num = 1
    
    # Find the highest existing number to determine the next number
    highest_existing_num = 0
    for existing_file in exact_matches:
        existing_stem = existing_file.stem
        match = re.match(rf'^{re.escape(base_stem)}\s*\((\d+)\)\s*$', existing_stem)
        if match:
            num = int(match.group(1))
            if num > highest_existing_num:
                highest_existing_num = num
    
    # Start from the next number after the highest existing
    if highest_existing_num > 0:
        next_num = highest_existing_num + 1
    
    # Find the next available number
    while True:
        new_stem = f"{base_stem} ({next_num})"
        new_path = parent / f"{new_stem}{suffix}"
        if not new_path.exists():
            return new_path
        next_num += 1


def _parse_cell_reference(cell_ref: str) -> tuple[int, int]:
    """Parse A1 cell reference to row and column indices.

    Args:
        cell_ref: A1 cell reference (e.g., 'A1', 'B10')

    Returns:
        Tuple of (row_index, col_index) where both are 0-based
    """
    # Extract column letters and row number
    col_str = ""
    row_str = ""
    
    for char in cell_ref:
        if char.isalpha():
            col_str += char.upper()
        elif char.isdigit():
            row_str += char
    
    # Convert column letters to index (A=0, B=1, AA=26, etc.)
    col_index = 0
    for char in col_str:
        col_index = col_index * 26 + (ord(char) - ord('A') + 1)
    col_index -= 1  # Make 0-based
    
    # Convert row string to index (make 0-based)
    row_index = int(row_str) - 1
    
    return row_index, col_index
