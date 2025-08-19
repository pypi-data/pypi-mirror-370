"""Generic spreadsheet utilities that work with both Google Sheets and Excel files.

This module provides high-level utilities that use the SpreadsheetInterface
to work seamlessly with both Google Sheets and Excel files.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from urarovite.core.spreadsheet import SpreadsheetFactory
from urarovite.core.exceptions import ValidationError


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
            spreadsheet.update_sheet_data(sheet_name, values, range_name=range_name)
            spreadsheet.save()
            return {"success": True, "error": None}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_spreadsheet_formulas(
    spreadsheet_source: Union[str, Path],
    auth_credentials: Optional[Dict[str, Any]] = None,
) -> Dict[str, Dict[str, str]]:
    """Get formulas from any spreadsheet source.

    Args:
        spreadsheet_source: Google Sheets URL or Excel file path
        auth_credentials: Authentication credentials (required for Google Sheets)

    Returns:
        Dict mapping sheet names to dict of cell coordinates to formulas
        Example: {"Sheet1": {"A1": "=SUM(B1:B10)", "B5": "=NOW()"}}
    """
    try:
        with SpreadsheetFactory.create_spreadsheet(
            spreadsheet_source, auth_credentials
        ) as spreadsheet:
            return spreadsheet.get_formulas()
    except Exception as e:
        raise ValidationError(f"Failed to get formulas: {str(e)}")


def rename_spreadsheet_sheet(
    spreadsheet_source: Union[str, Path],
    old_name: str,
    new_name: str,
    auth_credentials: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Rename a sheet in any spreadsheet source.

    Args:
        spreadsheet_source: Google Sheets URL or Excel file path
        old_name: Current name of the sheet
        new_name: New name for the sheet
        auth_credentials: Authentication credentials (required for Google Sheets)

    Returns:
        Dict with keys: success, error
    """
    try:
        with SpreadsheetFactory.create_spreadsheet(
            spreadsheet_source, auth_credentials
        ) as spreadsheet:
            spreadsheet.update_sheet_properties(old_name, new_name=new_name)
            spreadsheet.save()
            return {"success": True, "error": None}
    except Exception as e:
        return {"success": False, "error": str(e)}


def read_csv_data_from_spreadsheet(
    spreadsheet_source: Union[str, Path],
    sheet_name: Optional[str] = None,
    auth_credentials: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Read CSV-like data from any spreadsheet source and convert to list of dictionaries.

    Args:
        spreadsheet_source: Google Sheets URL or Excel file path
        sheet_name: Name of sheet to read (uses first sheet if None)
        auth_credentials: Authentication credentials (required for Google Sheets)

    Returns:
        List of dictionaries representing CSV rows
    """
    try:
        with SpreadsheetFactory.create_spreadsheet(
            spreadsheet_source, auth_credentials
        ) as spreadsheet:
            sheet_data = spreadsheet.get_sheet_data(sheet_name)
            values = sheet_data.values

        if not values or len(values) < 2:
            return []

        # First row is headers
        headers = values[0]
        csv_data = []

        # Convert rows to dictionaries
        for row_values in values[1:]:
            # Pad row with empty strings if needed
            while len(row_values) < len(headers):
                row_values.append("")

            # Create dictionary from headers and values
            row_dict = {}
            for i, header in enumerate(headers):
                if i < len(row_values):
                    row_dict[str(header)] = (
                        str(row_values[i]) if row_values[i] is not None else ""
                    )
                else:
                    row_dict[str(header)] = ""

            csv_data.append(row_dict)

        return csv_data

    except Exception as e:
        raise ValidationError(f"Failed to read CSV data: {str(e)}")


def write_json_to_spreadsheet(
    spreadsheet_source: Union[str, Path],
    json_data: List[Dict[str, Any]],
    sheet_name: Optional[str] = None,
    auth_credentials: Optional[Dict[str, Any]] = None,
) -> None:
    """Write JSON data to the next available column in any spreadsheet source.

    Args:
        spreadsheet_source: Google Sheets URL or Excel file path
        json_data: List of JSON objects to write
        sheet_name: Name of sheet to write to (uses first sheet if None)
        auth_credentials: Authentication credentials (required for Google Sheets)
    """
    try:
        with SpreadsheetFactory.create_spreadsheet(
            spreadsheet_source, auth_credentials, read_only=False
        ) as spreadsheet:
            # Get metadata to find available sheets
            metadata = spreadsheet.get_metadata()
            if not metadata.sheet_names:
                raise ValidationError("No sheets available for writing JSON output")

            # Use specified sheet or first sheet
            target_sheet = sheet_name or metadata.sheet_names[0]

            # Get next available column
            col_letter = spreadsheet.get_next_available_column(target_sheet)

            # Prepare JSON output data
            json_output_values = [["JSON_Output"]]  # Header
            for json_obj in json_data:
                json_str = json.dumps(json_obj, ensure_ascii=False)
                json_output_values.append([json_str])

            # Write to the next available column
            range_name = f"{col_letter}1:{col_letter}{len(json_output_values)}"
            spreadsheet.update_sheet_data(
                sheet_name=target_sheet,
                values=json_output_values,
                range_name=range_name,
            )
            spreadsheet.save()

    except Exception as e:
        raise ValidationError(f"Failed to write JSON data: {str(e)}")


def convert_google_sheets_to_excel(
    google_sheets_url: str,
    excel_file_path: Union[str, Path],
    auth_credentials: Dict[str, Any],
    sheet_names: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Convert Google Sheets to Excel file.

    Args:
        google_sheets_url: URL of the Google Sheets document
        excel_file_path: Path where Excel file should be saved (if "auto", uses original sheet name)
        auth_credentials: Authentication credentials for Google Sheets
        sheet_names: Optional list of specific sheets to convert
                    (converts all if None)

    Returns:
        Dict with keys: success, converted_sheets, error, output_path
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

        converted_sheets = []

        # Read from Google Sheets
        with SpreadsheetFactory.create_spreadsheet(
            google_sheets_url, auth_credentials
        ) as source_spreadsheet:
            source_metadata = source_spreadsheet.get_metadata()

            # Determine which sheets to convert
            sheets_to_convert = (
                sheet_names if sheet_names else source_metadata.sheet_names
            )

            # Create Excel file
            with SpreadsheetFactory.create_spreadsheet(
                excel_path, read_only=False, create_new=True
            ) as target_spreadsheet:
                # Get initial target metadata to check for existing sheets
                initial_metadata = target_spreadsheet.get_metadata()
                existing_sheets = set(initial_metadata.sheet_names)

                # Convert each sheet first
                for sheet_name in sheets_to_convert:
                    try:
                        # Get data from Google Sheets
                        sheet_data = source_spreadsheet.get_sheet_data(sheet_name)

                        # Create sheet in Excel file (only if it doesn't exist)
                        if sheet_name not in existing_sheets:
                            target_spreadsheet.create_sheet(sheet_name)

                        # Copy data (whether sheet existed or was just created)
                        if sheet_data.values:
                            target_spreadsheet.update_sheet_data(
                                sheet_name, sheet_data.values
                            )

                        converted_sheets.append(sheet_name)

                    except Exception as e:
                        # Log individual sheet errors but continue
                        import logging

                        logging.warning(f"Failed to convert sheet '{sheet_name}': {e}")

                # Remove sheets that existed initially but weren't converted from source
                if converted_sheets:
                    try:
                        final_metadata = target_spreadsheet.get_metadata()
                        sheets_to_remove = []

                        # Find sheets that were in the initial target but not converted
                        for sheet_name in existing_sheets:
                            if (
                                sheet_name not in converted_sheets
                                and sheet_name in final_metadata.sheet_names
                                and len(final_metadata.sheet_names) > 1
                            ):
                                sheets_to_remove.append(sheet_name)

                        # Remove unused initial sheets
                        for sheet_name in sheets_to_remove:
                            target_spreadsheet.delete_sheet(sheet_name)
                            import logging

                            logging.info(f"Removed unused initial sheet: {sheet_name}")

                    except Exception as e:
                        import logging

                        logging.warning(f"Could not remove unused sheets: {e}")

                # Save the Excel file
                target_spreadsheet.save()

        return {
            "success": True,
            "converted_sheets": converted_sheets,
            "output_path": str(excel_path),
            "error": None,
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
        )

    except Exception as e:
        return {"success": False, "converted_sheets": [], "error": str(e)}


def convert_excel_to_google_sheets_bulk(
    excel_file_path: Union[str, Path],
    google_sheets_url: str,
    auth_credentials: Dict[str, Any],
    sheet_names: Optional[List[str]] = None,
    create_new_sheets: bool = True,
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

    Returns:
        Dict with keys: success, converted_sheets, error
    """
    try:
        from urarovite.utils.sheets import extract_sheet_id
        from urarovite.auth.google_sheets import (
            create_sheets_service_from_encoded_creds,
        )

        excel_path = Path(excel_file_path)
        spreadsheet_id = extract_sheet_id(google_sheets_url)

        if not spreadsheet_id:
            raise ValidationError(f"Invalid Google Sheets URL: {google_sheets_url}")

        # Extract auth credentials
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

        return {"success": True, "converted_sheets": converted_sheets, "error": None}

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
) -> Union[str, Path]:
    """Resolve target name using original source name if target is 'auto'.

    Args:
        source: Source spreadsheet (Google Sheets URL or Excel file path)
        target: Target path or 'auto' for automatic naming
        auth_credentials: Auth credentials for Google Sheets access

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
                return Path(f"{clean_name}.xlsx")
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
            # Google Sheets source
            return Path("Converted_Spreadsheet.xlsx")


def convert_spreadsheet_format(
    source: Union[str, Path],
    target: Union[str, Path],
    auth_credentials: Optional[Dict[str, Any]] = None,
    sheet_names: Optional[List[str]] = None,
    preserve_formulas: bool = True,  # DEFAULT: Always preserve formulas
    preserve_visual_formatting: bool = True,  # DEFAULT: Always preserve visual formatting
    source_file_type: Optional[str] = None,  # Override automatic type detection
    target_file_type: Optional[str] = None,  # Override automatic type detection
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
        **kwargs: Additional arguments passed to specific conversion functions

    Returns:
        Dict with keys: success, conversion_type, converted_sheets,
                       formula_stats (if preserve_formulas=True),
                       formatting_stats (if preserve_visual_formatting=True), error
    """
    try:
        # Resolve target name if 'auto' is specified
        target = _resolve_target_name(source, target, auth_credentials)

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
    auth_credentials: Dict[str, Any],
    sheet_names: Optional[List[str]] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Copy data between Google Sheets documents."""
    try:
        converted_sheets = []

        with SpreadsheetFactory.create_spreadsheet(
            source_url, auth_credentials
        ) as source_spreadsheet:
            source_metadata = source_spreadsheet.get_metadata()
            sheets_to_copy = sheet_names if sheet_names else source_metadata.sheet_names

            with SpreadsheetFactory.create_spreadsheet(
                target_url, auth_credentials
            ) as target_spreadsheet:
                target_metadata = target_spreadsheet.get_metadata()
                existing_sheets = set(target_metadata.sheet_names)

                for sheet_name in sheets_to_copy:
                    try:
                        sheet_data = source_spreadsheet.get_sheet_data(sheet_name)

                        if sheet_name not in existing_sheets:
                            target_spreadsheet.create_sheet(sheet_name)

                        if sheet_data.values:
                            target_spreadsheet.update_sheet_data(
                                sheet_name, sheet_data.values
                            )

                        converted_sheets.append(sheet_name)

                    except Exception as e:
                        import logging

                        logging.warning(f"Failed to copy sheet '{sheet_name}': {e}")

        return {"success": True, "converted_sheets": converted_sheets, "error": None}

    except Exception as e:
        return {"success": False, "converted_sheets": [], "error": str(e)}


def _copy_excel_to_excel(
    source_path: Union[str, Path],
    target_path: Union[str, Path],
    sheet_names: Optional[List[str]] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Copy data between Excel files."""
    try:
        source_path = Path(source_path)
        target_path = Path(target_path)

        # Ensure target directory exists
        target_path.parent.mkdir(parents=True, exist_ok=True)

        # Ensure .xlsx extension for target
        if target_path.suffix.lower() not in [".xlsx", ".xls", ".xlsm"]:
            target_path = target_path.with_suffix(".xlsx")

        converted_sheets = []

        with SpreadsheetFactory.create_spreadsheet(
            source_path, read_only=True
        ) as source_spreadsheet:
            source_metadata = source_spreadsheet.get_metadata()
            sheets_to_copy = sheet_names if sheet_names else source_metadata.sheet_names

            with SpreadsheetFactory.create_spreadsheet(
                target_path, read_only=False, create_new=True
            ) as target_spreadsheet:
                for sheet_name in sheets_to_copy:
                    try:
                        sheet_data = source_spreadsheet.get_sheet_data(sheet_name)

                        target_spreadsheet.create_sheet(sheet_name)

                        if sheet_data.values:
                            target_spreadsheet.update_sheet_data(
                                sheet_name, sheet_data.values
                            )

                        converted_sheets.append(sheet_name)

                    except Exception as e:
                        import logging

                        logging.warning(f"Failed to copy sheet '{sheet_name}': {e}")

                # Remove default sheet AFTER adding all copied sheets
                if converted_sheets:
                    try:
                        target_metadata = target_spreadsheet.get_metadata()
                        for default_name in ["Sheet", "Sheet1"]:
                            if (
                                default_name in target_metadata.sheet_names
                                and default_name not in converted_sheets
                                and len(target_metadata.sheet_names) > 1
                            ):
                                target_spreadsheet.delete_sheet(default_name)
                                import logging

                                logging.info(f"Removed default sheet: {default_name}")
                    except Exception as e:
                        import logging

                        logging.warning(f"Could not remove default sheet: {e}")

                target_spreadsheet.save()

        return {
            "success": True,
            "converted_sheets": converted_sheets,
            "output_path": str(target_path),
            "error": None,
        }

    except Exception as e:
        return {
            "success": False,
            "converted_sheets": [],
            "output_path": None,
            "error": str(e),
        }
