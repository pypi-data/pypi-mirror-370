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
    duplicate_file_to_drive_folder,
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
    "duplicate_file_to_drive_folder",
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
]
