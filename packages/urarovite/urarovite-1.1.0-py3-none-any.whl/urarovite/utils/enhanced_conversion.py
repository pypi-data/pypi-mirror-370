"""Enhanced spreadsheet conversion with full visual formatting preservation.

This module provides conversion functions that preserve both data/formulas AND
visual formatting (fonts, colors, borders, alignment) when converting between
Excel and Google Sheets.
"""

import logging
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

from urarovite.core.spreadsheet import SpreadsheetFactory
from urarovite.core.exceptions import ValidationError
from urarovite.utils.format_preservation import (
    FormatExtractor,
    FormatApplier,
    preserve_formatting_during_conversion,
)

logger = logging.getLogger(__name__)


def convert_with_full_formatting(
    source: Union[str, Path],
    target: Union[str, Path],
    auth_credentials: Optional[Dict[str, Any]] = None,
    sheet_names: Optional[List[str]] = None,
    preserve_formulas: bool = True,
    preserve_visual_formatting: bool = True,
    source_file_type: Optional[str] = None,  # Override automatic type detection
    target_file_type: Optional[str] = None,  # Override automatic type detection
) -> Dict[str, Any]:
    """Convert spreadsheet with complete formatting preservation.

    This function preserves:
    - Data values and formulas (if preserve_formulas=True)
    - Visual formatting: fonts, colors, borders, alignment (if preserve_visual_formatting=True)
    - Structural elements: sheets, ranges, merged cells

    Args:
        source: Source spreadsheet (Google Sheets URL or Excel file path)
        target: Target spreadsheet (Google Sheets URL or Excel file path)
        auth_credentials: Authentication credentials (required for Google Sheets)
        sheet_names: Optional list of specific sheets to convert
        preserve_formulas: Whether to preserve formulas and references
        preserve_visual_formatting: Whether to preserve fonts, colors, borders, etc.

    Returns:
        Dict with keys: success, converted_sheets, formatting_stats, formula_stats, error
    """
    try:
        result = {
            "success": False,
            "converted_sheets": [],
            "formatting_stats": {
                "cells_with_formatting": 0,
                "formats_preserved": 0,
                "formats_translated": 0,
                "formats_failed": 0,
            },
            "formula_stats": {
                "total_formulas": 0,
                "preserved_formulas": 0,
                "failed_formulas": 0,
            },
            "error": None,
        }

        # Determine source and target formats (with override support)
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

        logger.info(
            f"Converting {'Google Sheets' if source_is_google else 'Excel'} → {'Google Sheets' if target_is_google else 'Excel'}"
        )

        # Initialize format extractor and applier
        format_extractor = FormatExtractor()
        format_applier = FormatApplier()

        # Step 1: Handle Excel files on Google Drive by downloading them first
        actual_source = source
        temp_source_file = None

        # Check if this is an Excel file hosted on Google Drive
        if (
            not source_is_google
            and isinstance(source, str)
            and ("drive.google.com" in source or "docs.google.com" in source)
        ):
            # This is an Excel file on Google Drive - download it first
            logger.info("Downloading Excel file from Google Drive...")
            import tempfile
            import os
            from urarovite.utils.drive import download_file_from_drive

            if not auth_credentials:
                raise ValidationError(
                    "Authentication required to download Excel file from Google Drive"
                )

            # Create temporary file for download
            temp_source_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
            temp_source_file.close()

            # Download the file
            download_result = download_file_from_drive(
                source, temp_source_file.name, auth_credentials
            )
            if not download_result.get("success", False):
                os.unlink(temp_source_file.name)
                raise ValidationError(
                    f"Failed to download Excel file: {download_result.get('error', 'Unknown error')}"
                )

            actual_source = temp_source_file.name
            logger.info(f"Downloaded to temporary file: {actual_source}")

        # Step 2: Create source spreadsheet and extract data + formatting
        source_kwargs = {}
        if not source_is_google:
            source_kwargs["preserve_formulas"] = preserve_formulas
            source_kwargs["read_only"] = True  # Read-only for source

        try:
            with SpreadsheetFactory.create_spreadsheet(
                actual_source,
                auth_credentials if source_is_google else None,
                **source_kwargs,
            ) as source_spreadsheet:
                source_metadata = source_spreadsheet.get_metadata()
                sheets_to_convert = (
                    sheet_names if sheet_names else source_metadata.sheet_names
                )

                logger.info(
                    f"Converting {len(sheets_to_convert)} sheets: {sheets_to_convert}"
                )

                # Step 2: Create target spreadsheet
                target_kwargs = {}
                if not target_is_google:
                    target_kwargs["preserve_formulas"] = preserve_formulas
                    target_kwargs["read_only"] = False  # Write mode for target
                    target_kwargs["create_new"] = True

                with SpreadsheetFactory.create_spreadsheet(
                    target, auth_credentials, **target_kwargs
                ) as target_spreadsheet:
                    # Step 3: Convert each sheet with full formatting
                    for sheet_name in sheets_to_convert:
                        try:
                            sheet_result = _convert_sheet_with_formatting(
                                source_spreadsheet=source_spreadsheet,
                                target_spreadsheet=target_spreadsheet,
                                sheet_name=sheet_name,
                                source_is_google=source_is_google,
                                target_is_google=target_is_google,
                                preserve_formulas=preserve_formulas,
                                preserve_visual_formatting=preserve_visual_formatting,
                                format_extractor=format_extractor,
                                format_applier=format_applier,
                                auth_credentials=auth_credentials,
                            )

                            if sheet_result["success"]:
                                result["converted_sheets"].append(sheet_name)

                                # Aggregate stats
                                result["formatting_stats"]["cells_with_formatting"] += (
                                    sheet_result["formatting_stats"][
                                        "cells_with_formatting"
                                    ]
                                )
                                result["formatting_stats"]["formats_preserved"] += (
                                    sheet_result["formatting_stats"][
                                        "formats_preserved"
                                    ]
                                )
                                result["formatting_stats"]["formats_translated"] += (
                                    sheet_result["formatting_stats"][
                                        "formats_translated"
                                    ]
                                )
                                result["formatting_stats"]["formats_failed"] += (
                                    sheet_result["formatting_stats"]["formats_failed"]
                                )

                                result["formula_stats"]["total_formulas"] += (
                                    sheet_result["formula_stats"]["total_formulas"]
                                )
                                result["formula_stats"]["preserved_formulas"] += (
                                    sheet_result["formula_stats"]["preserved_formulas"]
                                )
                                result["formula_stats"]["failed_formulas"] += (
                                    sheet_result["formula_stats"]["failed_formulas"]
                                )

                            else:
                                logger.warning(
                                    f"Failed to convert sheet {sheet_name}: {sheet_result['error']}"
                                )

                        except Exception as e:
                            logger.error(f"Error converting sheet {sheet_name}: {e}")
                            result["formatting_stats"]["formats_failed"] += 1

                    # Step 4: Save target spreadsheet
                    target_spreadsheet.save()

                    # Step 4.5: Remove default sheets that weren't converted from source
                    if result["converted_sheets"] and target_is_google:
                        try:
                            final_metadata = target_spreadsheet.get_metadata()
                            for default_name in ["Sheet", "Sheet1"]:
                                if (
                                    default_name in final_metadata.sheet_names
                                    and default_name not in result["converted_sheets"]
                                    and len(final_metadata.sheet_names) > 1
                                ):
                                    target_spreadsheet.delete_sheet(default_name)
                                    logger.info(
                                        f"Removed unused default sheet: {default_name}"
                                    )
                        except Exception as e:
                            logger.warning(f"Could not remove default sheet: {e}")

            # Step 5: Finalize results
            if result["converted_sheets"]:
                result["success"] = True
                logger.info(
                    f"Successfully converted {len(result['converted_sheets'])} sheets with formatting"
                )
            else:
                result["error"] = "No sheets were successfully converted"

            return result

        except Exception as e:
            result["error"] = f"Conversion failed: {str(e)}"
            result["success"] = False
            logger.error(f"Inner conversion failed: {e}")
            return result

    except Exception as e:
        logger.error(f"Conversion with formatting failed: {e}")
        return {
            "success": False,
            "converted_sheets": [],
            "formatting_stats": {
                "cells_with_formatting": 0,
                "formats_preserved": 0,
                "formats_translated": 0,
                "formats_failed": 0,
            },
            "formula_stats": {
                "total_formulas": 0,
                "preserved_formulas": 0,
                "failed_formulas": 0,
            },
            "error": str(e),
        }
    finally:
        # Clean up temporary file if it was created
        if temp_source_file and os.path.exists(temp_source_file.name):
            try:
                import os

                os.unlink(temp_source_file.name)
                logger.info("Cleaned up temporary downloaded file")
            except Exception as e:
                logger.warning(f"Failed to clean up temporary file: {e}")


def _convert_sheet_with_formatting(
    source_spreadsheet: Any,
    target_spreadsheet: Any,
    sheet_name: str,
    source_is_google: bool,
    target_is_google: bool,
    preserve_formulas: bool,
    preserve_visual_formatting: bool,
    format_extractor: FormatExtractor,
    format_applier: FormatApplier,
    auth_credentials: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    """Convert a single sheet with complete formatting preservation."""

    sheet_result = {
        "success": False,
        "formatting_stats": {
            "cells_with_formatting": 0,
            "formats_preserved": 0,
            "formats_translated": 0,
            "formats_failed": 0,
        },
        "formula_stats": {
            "total_formulas": 0,
            "preserved_formulas": 0,
            "failed_formulas": 0,
        },
        "error": None,
    }

    try:
        logger.info(f"Converting sheet: {sheet_name}")

        # Step 1: Get sheet data from source
        source_data = source_spreadsheet.get_sheet_data(sheet_name)
        if not source_data or not source_data.values:
            logger.warning(f"No data found in sheet {sheet_name}")
            return sheet_result

        # Step 2: Extract visual formatting if requested
        source_formats = {}
        if preserve_visual_formatting:
            try:
                if source_is_google:
                    # Extract from Google Sheets
                    sheets_service = getattr(source_spreadsheet, "sheets_service", None)
                    spreadsheet_id = getattr(source_spreadsheet, "spreadsheet_id", None)
                    if sheets_service and spreadsheet_id:
                        source_formats = (
                            format_extractor.extract_google_sheets_formatting(
                                sheets_service, spreadsheet_id, sheet_name
                            )
                        )
                else:
                    # Extract from Excel
                    workbook = getattr(source_spreadsheet, "workbook", None)
                    if workbook:
                        source_formats = format_extractor.extract_excel_formatting(
                            workbook, sheet_name
                        )

                sheet_result["formatting_stats"]["cells_with_formatting"] = len(
                    source_formats
                )
                logger.info(f"Extracted formatting from {len(source_formats)} cells")

            except Exception as e:
                logger.warning(f"Failed to extract formatting from {sheet_name}: {e}")
                sheet_result["formatting_stats"]["formats_failed"] = 1

        # Step 3: Extract formulas if requested
        source_formulas = {}
        if preserve_formulas:
            try:
                source_formulas = source_spreadsheet.get_sheet_formulas(sheet_name)
                sheet_result["formula_stats"]["total_formulas"] = len(source_formulas)
                logger.info(f"Extracted {len(source_formulas)} formulas")
            except Exception as e:
                logger.warning(f"Failed to extract formulas from {sheet_name}: {e}")

        # Step 4: Create/update target sheet with data
        try:
            # Create sheet if it doesn't exist
            target_metadata = target_spreadsheet.get_metadata()
            if sheet_name not in target_metadata.sheet_names:
                target_spreadsheet.create_sheet(sheet_name)

            # Update sheet data
            target_spreadsheet.update_sheet_data(
                sheet_name=sheet_name,
                values=source_data.values,
                start_row=1,
                start_col=1,
            )

        except Exception as e:
            sheet_result["error"] = f"Failed to update sheet data: {e}"
            return sheet_result

        # Step 5: Apply formulas to target
        if preserve_formulas and source_formulas:
            try:
                # Translate formulas if needed
                if source_is_google != target_is_google:
                    from urarovite.utils.formula_aware_conversion import (
                        _process_formulas_for_target,
                    )

                    formula_result = _process_formulas_for_target(
                        source_formulas,
                        sheet_name,
                        source_is_google,
                        target_is_google,
                        True,
                    )
                    translated_formulas = formula_result["formulas"]
                    sheet_result["formula_stats"]["preserved_formulas"] = (
                        len(translated_formulas) - formula_result["failed_count"]
                    )
                    sheet_result["formula_stats"]["failed_formulas"] = formula_result[
                        "failed_count"
                    ]
                else:
                    translated_formulas = source_formulas
                    sheet_result["formula_stats"]["preserved_formulas"] = len(
                        translated_formulas
                    )

                # Apply formulas to target
                target_spreadsheet.update_sheet_formulas(
                    sheet_name, translated_formulas
                )

            except Exception as e:
                logger.warning(f"Failed to apply formulas to {sheet_name}: {e}")
                sheet_result["formula_stats"]["failed_formulas"] = len(source_formulas)

        # Step 6: Apply visual formatting to target
        if preserve_visual_formatting and source_formats:
            try:
                # Translate formatting between platforms
                translated_formats = preserve_formatting_during_conversion(
                    source_formats, source_is_google, target_is_google
                )

                sheet_result["formatting_stats"]["formats_translated"] = len(
                    translated_formats
                )

                # Apply formatting to target
                if target_is_google:
                    # Apply to Google Sheets
                    sheets_service = getattr(target_spreadsheet, "sheets_service", None)
                    spreadsheet_id = getattr(target_spreadsheet, "spreadsheet_id", None)
                    if sheets_service and spreadsheet_id:
                        # Get sheet ID for the target sheet
                        sheet_id = _get_google_sheet_id(
                            sheets_service, spreadsheet_id, sheet_name
                        )

                        if sheet_id is not None:
                            format_applier.apply_google_sheets_formatting(
                                sheets_service,
                                spreadsheet_id,
                                sheet_id,
                                translated_formats,
                            )
                            sheet_result["formatting_stats"]["formats_preserved"] = len(
                                translated_formats
                            )
                else:
                    # Apply to Excel
                    workbook = getattr(target_spreadsheet, "workbook", None)
                    if workbook:
                        format_applier.apply_excel_formatting(
                            workbook, sheet_name, translated_formats
                        )
                        sheet_result["formatting_stats"]["formats_preserved"] = len(
                            translated_formats
                        )

            except Exception as e:
                logger.warning(f"Failed to apply formatting to {sheet_name}: {e}")
                sheet_result["formatting_stats"]["formats_failed"] = len(source_formats)

        sheet_result["success"] = True
        return sheet_result

    except Exception as e:
        sheet_result["error"] = str(e)
        return sheet_result


def _get_google_sheet_id(
    sheets_service: Any, spreadsheet_id: str, sheet_name: str
) -> Optional[int]:
    """Get the internal sheet ID for a given sheet name in Google Sheets.

    Args:
        sheets_service: Google Sheets API service
        spreadsheet_id: ID of the spreadsheet
        sheet_name: Name of the sheet

    Returns:
        Internal sheet ID (integer) or None if not found
    """
    try:
        # Get spreadsheet metadata
        response = (
            sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        )

        # Find the sheet with the matching name
        for sheet in response.get("sheets", []):
            properties = sheet.get("properties", {})
            if properties.get("title") == sheet_name:
                return properties.get("sheetId")

        logger.warning(f"Sheet '{sheet_name}' not found in spreadsheet")
        return None

    except Exception as e:
        logger.error(f"Failed to get sheet ID for '{sheet_name}': {e}")
        return None


def convert_with_enhanced_formatting(
    source: Union[str, Path],
    target: Union[str, Path],
    auth_credentials: Optional[Dict[str, Any]] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Enhanced wrapper that enables full formatting preservation by default.

    This is a drop-in replacement for convert_spreadsheet_format that adds
    visual formatting preservation.
    """
    return convert_with_full_formatting(
        source=source,
        target=target,
        auth_credentials=auth_credentials,
        preserve_formulas=kwargs.get("preserve_formulas", True),
        preserve_visual_formatting=kwargs.get("preserve_visual_formatting", True),
        sheet_names=kwargs.get("sheet_names"),
    )
