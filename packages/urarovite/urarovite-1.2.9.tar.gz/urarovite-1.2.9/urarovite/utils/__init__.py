"""Utility modules for the Urarovite validation library."""

from urarovite.utils.sheets import (
    extract_sheet_id,
    split_segments,
    strip_outer_single_quotes,
    extract_sheet_and_range,
    parse_tab_token,
    parse_referenced_tabs,
    col_index_to_letter,
    letter_to_col_index,
    fetch_sheet_tabs,
    get_sheet_values,
    update_sheet_values,
    duplicate_sheets_from_sheet_urls_in_range,
    fetch_workbook_with_formulas,
    get_segment_separator,
    set_segment_separator,
)

from urarovite.utils.gsheets_to_xlsx import GSheetToXlsx
from urarovite.utils.xlsx_to_gsheets import XlsxToGSheets
from urarovite.utils.drive import (
    # Core file operations
    extract_google_file_id,
    extract_folder_id,
    get_parent_folder_id,
    get_file_metadata,
    download_file_from_drive,
    upload_file_to_drive_folder,
    duplicate_file_to_drive_folder,
    move_sheets_to_folder,
    # File type detection
    detect_spreadsheet_type,
    # Filename extraction
    extract_original_filename_from_source,
    # Backward compatibility aliases
    download_drive_file,
    get_drive_file_metadata,
)

from urarovite.utils.generic_spreadsheet import (
    get_spreadsheet_tabs,
    get_spreadsheet_data,
    update_spreadsheet_data,
    get_spreadsheet_formulas,
    rename_spreadsheet_sheet,
    read_csv_data_from_spreadsheet,
    write_json_to_spreadsheet,
)

from urarovite.utils.tab_name_sanitizer import (
    sanitize_tab_name,
    detect_non_alphanumeric_tabs,
    ensure_unique_names,
    analyze_tab_names_for_sanitization,
    get_spreadsheet_tab_analysis,
    sanitize_spreadsheet_tab_names,
)

from urarovite.utils.tab_renamer import (
    rename_single_tab,
    rename_multiple_tabs,
    analyze_tab_rename_requirements,
    update_a1_references_in_spreadsheet,
    rename_tab_with_a1_format_fix,
)

from .a1_range_validator import (
    validate_a1_ranges,
    fix_a1_ranges,
    get_a1_validation_examples,
    update_a1_references_in_text,
    update_a1_references_in_spreadsheet_cells,
)

__all__ = [
    # Sheet URL and range parsing
    "extract_sheet_id",
    "split_segments",
    "strip_outer_single_quotes",
    "extract_sheet_and_range",
    "parse_tab_token",
    "parse_referenced_tabs",
    # Column conversions
    "col_index_to_letter",
    "letter_to_col_index",
    # Sheet data access
    "fetch_sheet_tabs",
    "get_sheet_values",
    "update_sheet_values",
    # GSheets to XLSX
    "GSheetToXlsx",
    # XLSX to GSheets
    "XlsxToGSheets",
    "duplicate_sheets_from_sheet_urls_in_range",
    "fetch_workbook_with_formulas",
    # Generic spreadsheet utilities
    "get_spreadsheet_tabs",
    "get_spreadsheet_data",
    "update_spreadsheet_data",
    "get_spreadsheet_formulas",
    "rename_spreadsheet_sheet",
    "read_csv_data_from_spreadsheet",
    "write_json_to_spreadsheet",
    # Sheets and Drive utilities
    "get_segment_separator",
    "set_segment_separator",
    # Drive utilities
    "extract_google_file_id",
    "extract_folder_id",
    "get_parent_folder_id",
    "get_file_metadata",
    "download_file_from_drive",
    "upload_file_to_drive_folder",
    "duplicate_file_to_drive_folder",
    "move_sheets_to_folder",
    "detect_spreadsheet_type",
    "extract_original_filename_from_source",
    # Backward compatibility
    "download_drive_file",
    "get_drive_file_metadata",
    # Tab name sanitization utilities
    "sanitize_tab_name",
    "detect_non_alphanumeric_tabs",
    "ensure_unique_names",
    "analyze_tab_names_for_sanitization",
    "get_spreadsheet_tab_analysis",
    "sanitize_spreadsheet_tab_names",
    # Tab renaming utilities
    "rename_single_tab",
    "rename_multiple_tabs",
    "analyze_tab_rename_requirements",
    "update_a1_references_in_spreadsheet",
    # A1 range validation utilities
    "validate_a1_ranges",
    "fix_a1_ranges",
    "get_a1_validation_examples",
    "update_a1_references_in_text",
    "update_a1_references_in_spreadsheet_cells",  # New shared utility
]
