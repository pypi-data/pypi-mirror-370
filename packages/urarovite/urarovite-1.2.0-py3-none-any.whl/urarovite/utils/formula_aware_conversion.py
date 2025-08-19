"""Formula-aware spreadsheet conversion utilities.

This module provides conversion functions that preserve formulas and cell references
during spreadsheet format conversion, ensuring data integrity and functionality.
"""

import re
from typing import Any, Dict, List, Optional, Union, Tuple
from pathlib import Path

from urarovite.core.spreadsheet import SpreadsheetFactory
from urarovite.core.exceptions import ValidationError


def convert_with_formulas(
    source: Union[str, Path],
    target: Union[str, Path],
    auth_credentials: Optional[Dict[str, Any]] = None,
    sheet_names: Optional[List[str]] = None,
    translate_references: bool = True,
    source_file_type: Optional[str] = None,  # Override automatic type detection
    target_file_type: Optional[str] = None,  # Override automatic type detection
) -> Dict[str, Any]:
    """Convert spreadsheet while preserving formulas and references.

    Args:
        source: Source spreadsheet (Google Sheets URL or Excel file path)
        target: Target spreadsheet (Google Sheets URL or Excel file path)
        auth_credentials: Authentication credentials (required for Google Sheets)
        sheet_names: Optional list of specific sheets to convert
        translate_references: Whether to translate cross-sheet references

    Returns:
        Dict with keys: success, converted_sheets, formula_stats, error
    """
    try:
        converted_sheets = []
        formula_stats = {
            "total_formulas": 0,
            "translated_references": 0,
            "preserved_formulas": 0,
            "failed_formulas": 0,
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

        # Create source spreadsheet with formula preservation
        source_kwargs = {}
        if not source_is_google:
            source_kwargs["preserve_formulas"] = True

        with SpreadsheetFactory.create_spreadsheet(
            source, auth_credentials, **source_kwargs
        ) as source_spreadsheet:
            source_metadata = source_spreadsheet.get_metadata()
            sheets_to_convert = (
                sheet_names if sheet_names else source_metadata.sheet_names
            )

            # Create target spreadsheet with formula support
            target_kwargs = {}
            if not target_is_google:
                target_kwargs["preserve_formulas"] = (
                    True  # CRITICAL: Enable formula support
                )
                target_kwargs["read_only"] = False
                target_kwargs["create_new"] = (
                    True  # CRITICAL: Allow creating new Excel files
                )

            with SpreadsheetFactory.create_spreadsheet(
                target, auth_credentials, **target_kwargs
            ) as target_spreadsheet:
                # Get initial target metadata to check for existing sheets
                if not target_is_google:
                    initial_metadata = target_spreadsheet.get_metadata()
                    existing_sheets = set(initial_metadata.sheet_names)
                else:
                    existing_sheets = set()

                # Convert each sheet with formulas
                for sheet_name in sheets_to_convert:
                    try:
                        # Get data and formulas from source
                        sheet_data_with_formulas = (
                            source_spreadsheet.get_sheet_data_with_formulas(sheet_name)
                        )

                        # Create sheet in target (only if it doesn't exist)
                        if not target_is_google and sheet_name not in existing_sheets:
                            target_spreadsheet.create_sheet(sheet_name)
                        elif target_is_google:
                            target_spreadsheet.create_sheet(sheet_name)

                        # Copy values first
                        if sheet_data_with_formulas["values"]:
                            target_spreadsheet.update_sheet_data(
                                sheet_name, sheet_data_with_formulas["values"]
                            )

                        # Process and copy formulas
                        source_formulas = sheet_data_with_formulas["formulas"]
                        if source_formulas:
                            processed_formulas = _process_formulas_for_target(
                                source_formulas,
                                sheet_name,
                                source_is_google,
                                target_is_google,
                                translate_references,
                            )

                            # Update formula stats
                            formula_stats["total_formulas"] += len(source_formulas)
                            formula_stats["translated_references"] += (
                                processed_formulas["translated_count"]
                            )
                            formula_stats["preserved_formulas"] += len(
                                processed_formulas["formulas"]
                            )
                            formula_stats["failed_formulas"] += processed_formulas[
                                "failed_count"
                            ]

                            # Set formulas in target
                            if processed_formulas["formulas"]:
                                target_spreadsheet.update_sheet_formulas(
                                    sheet_name,
                                    processed_formulas["formulas"],
                                    preserve_values=True,
                                )

                        converted_sheets.append(sheet_name)

                    except Exception as e:
                        # Log individual sheet errors but continue
                        import logging

                        logging.warning(
                            f"Failed to convert sheet '{sheet_name}' with formulas: {e}"
                        )

                # Remove sheets that existed initially but weren't converted from source
                if converted_sheets and not target_is_google:
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

                # Save the target spreadsheet
                target_spreadsheet.save()

        return {
            "success": True,
            "converted_sheets": converted_sheets,
            "formula_stats": formula_stats,
            "output_path": str(target) if isinstance(target, Path) else target,
            "error": None,
        }

    except Exception as e:
        return {
            "success": False,
            "converted_sheets": [],
            "formula_stats": {},
            "output_path": None,
            "error": str(e),
        }


def _process_formulas_for_target(
    formulas: Dict[str, str],
    sheet_name: str,
    source_is_google: bool,
    target_is_google: bool,
    translate_references: bool,
) -> Dict[str, Any]:
    """Process formulas for target format compatibility.

    Args:
        formulas: Dict mapping cell coordinates to formulas
        sheet_name: Name of the current sheet
        source_is_google: Whether source is Google Sheets
        target_is_google: Whether target is Google Sheets
        translate_references: Whether to translate references

    Returns:
        Dict with processed formulas and statistics
    """
    processed_formulas = {}
    translated_count = 0
    failed_count = 0

    for cell_ref, formula in formulas.items():
        try:
            processed_formula = formula

            if translate_references:
                # Translate cross-sheet references if needed
                if source_is_google != target_is_google:
                    processed_formula, was_translated = _translate_sheet_references(
                        formula, source_is_google, target_is_google
                    )
                    if was_translated:
                        translated_count += 1

                # Translate function names if needed
                processed_formula = _translate_function_names(
                    processed_formula, source_is_google, target_is_google
                )

            processed_formulas[cell_ref] = processed_formula

        except Exception as e:
            # Log failed formula but continue
            import logging

            logging.warning(
                f"Failed to process formula in {sheet_name}!{cell_ref}: {formula}. Error: {e}"
            )
            failed_count += 1

    return {
        "formulas": processed_formulas,
        "translated_count": translated_count,
        "failed_count": failed_count,
    }


def _translate_sheet_references(
    formula: str, source_is_google: bool, target_is_google: bool
) -> Tuple[str, bool]:
    """Translate cross-sheet references between Google Sheets and Excel formats.

    Args:
        formula: The formula to translate
        source_is_google: Whether source is Google Sheets
        target_is_google: Whether target is Google Sheets

    Returns:
        Tuple of (translated_formula, was_translated)
    """
    if source_is_google == target_is_google:
        return formula, False  # No translation needed

    translated = formula
    was_translated = False

    if source_is_google and not target_is_google:
        # Google Sheets → Excel: 'Sheet Name'!A1 → 'Sheet Name'!A1 (mostly compatible)
        # Main difference: Google Sheets allows spaces in sheet names without quotes sometimes
        # Excel always requires quotes for sheet names with spaces

        # Find sheet references without quotes and add them
        pattern = r"([^'\"]\s*)([A-Za-z0-9][A-Za-z0-9\s]*[A-Za-z0-9])(!)"
        matches = re.finditer(pattern, translated)

        for match in reversed(list(matches)):  # Reverse to maintain positions
            prefix, sheet_name, exclamation = match.groups()
            if " " in sheet_name and not (
                sheet_name.startswith("'") and sheet_name.endswith("'")
            ):
                # Add quotes around sheet name
                new_ref = f"{prefix}'{sheet_name}'{exclamation}"
                start, end = match.span()
                translated = translated[:start] + new_ref + translated[end:]
                was_translated = True

    elif not source_is_google and target_is_google:
        # Excel → Google Sheets: Generally compatible
        # Google Sheets is more flexible with sheet name references
        pass  # Most Excel references work in Google Sheets

    return translated, was_translated


def _translate_function_names(
    formula: str, source_is_google: bool, target_is_google: bool
) -> str:
    """Translate function names between Google Sheets and Excel.

    Args:
        formula: The formula to translate
        source_is_google: Whether source is Google Sheets
        target_is_google: Whether target is Google Sheets

    Returns:
        Translated formula
    """
    if source_is_google == target_is_google:
        return formula  # No translation needed

    # Function name mappings
    google_to_excel = {
        "ARRAYFORMULA": "",  # Excel doesn't have direct equivalent
        "IMPORTRANGE": "",  # Excel doesn't have direct equivalent
        "QUERY": "",  # Excel doesn't have direct equivalent
        "REGEXMATCH": "",  # Excel uses different regex functions
        "REGEXREPLACE": "",  # Excel uses different regex functions
    }

    excel_to_google = {
        # Most Excel functions work in Google Sheets
        # Google Sheets is generally more compatible
    }

    translated = formula

    if source_is_google and not target_is_google:
        # Google Sheets → Excel
        for google_func, excel_func in google_to_excel.items():
            if excel_func:  # Only translate if there's a direct equivalent
                pattern = rf"\b{google_func}\b"
                translated = re.sub(
                    pattern, excel_func, translated, flags=re.IGNORECASE
                )
            else:
                # Warn about unsupported functions
                if re.search(rf"\b{google_func}\b", translated, re.IGNORECASE):
                    import logging

                    logging.warning(
                        f"Formula contains Google Sheets-specific function '{google_func}' "
                        f"which has no Excel equivalent: {formula}"
                    )

    elif not source_is_google and target_is_google:
        # Excel → Google Sheets
        for excel_func, google_func in excel_to_google.items():
            pattern = rf"\b{excel_func}\b"
            translated = re.sub(pattern, google_func, translated, flags=re.IGNORECASE)

    return translated


def validate_formula_compatibility(
    formulas: Dict[str, str], source_format: str, target_format: str
) -> Dict[str, Any]:
    """Validate formula compatibility between formats.

    Args:
        formulas: Dict mapping cell coordinates to formulas
        source_format: Source format ("google_sheets" or "excel")
        target_format: Target format ("google_sheets" or "excel")

    Returns:
        Dict with compatibility analysis
    """
    compatibility_report = {
        "total_formulas": len(formulas),
        "compatible_formulas": 0,
        "incompatible_formulas": 0,
        "warnings": [],
        "incompatible_functions": set(),
        "cross_sheet_references": 0,
    }

    # Define incompatible functions
    google_only_functions = {
        "ARRAYFORMULA",
        "IMPORTRANGE",
        "QUERY",
        "REGEXMATCH",
        "REGEXREPLACE",
        "GOOGLETRANSLATE",
        "SPARKLINE",
        "IMAGE",
    }

    excel_only_functions = {"XLOOKUP", "XMATCH", "FILTER", "SORT", "UNIQUE", "SEQUENCE"}

    for cell_ref, formula in formulas.items():
        is_compatible = True

        # Check for cross-sheet references
        if "!" in formula:
            compatibility_report["cross_sheet_references"] += 1

        # Check for format-specific functions
        if source_format == "google_sheets" and target_format == "excel":
            for func in google_only_functions:
                if re.search(rf"\b{func}\b", formula, re.IGNORECASE):
                    is_compatible = False
                    compatibility_report["incompatible_functions"].add(func)
                    compatibility_report["warnings"].append(
                        f"Cell {cell_ref}: Google Sheets function '{func}' not available in Excel"
                    )

        elif source_format == "excel" and target_format == "google_sheets":
            for func in excel_only_functions:
                if re.search(rf"\b{func}\b", formula, re.IGNORECASE):
                    is_compatible = False
                    compatibility_report["incompatible_functions"].add(func)
                    compatibility_report["warnings"].append(
                        f"Cell {cell_ref}: Excel function '{func}' may not be available in Google Sheets"
                    )

        if is_compatible:
            compatibility_report["compatible_formulas"] += 1
        else:
            compatibility_report["incompatible_formulas"] += 1

    # Convert set to list for JSON serialization
    compatibility_report["incompatible_functions"] = list(
        compatibility_report["incompatible_functions"]
    )

    return compatibility_report
