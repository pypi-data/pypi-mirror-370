"""Validation criteria definitions for the Urarovite library.

This module defines all available validation criteria that can be applied
to Google Sheets data. Each criterion has an ID, name, and description.
"""

from typing import TypedDict


class ValidationCriterion(TypedDict):
    """Type definition for a validation criterion."""

    id: str
    name: str
    description: str
    supports_fix: bool
    supports_flag: bool


# All available validation criteria
VALIDATION_CRITERIA: list[ValidationCriterion] = [
    # Data Quality Validators
    {
        "id": "empty_cells",
        "name": "Fix Empty Cells",
        "description": "Identifies and optionally fills empty cells with default values",
        "supports_fix": True,
        "supports_flag": True,
    },
    {
        "id": "tab_names",
        "name": "Fix Tab Names",
        "description": (
            "Validates tab names for illegal characters and "
            "Excel length limits (31 chars). Fixes illegal characters "
            "and truncates long names with collision-safe suffixes."
        ),
        "supports_fix": True,
        "supports_flag": True,
    },
    {
        "id": "invalid_verification_ranges",
        "name": "Fix Verification Ranges",
        "description": (
            "Validates and fixes malformed A1 notation ranges. "
            "Automatically converts curly quotes (\" \" ' ') to straight "
            "quotes and ensures proper sheet name quoting."
        ),
        "supports_fix": True,
        "supports_flag": True,
    },
    # Spreadsheet Range Validators
    {
        "id": "sheet_name_quoting",
        "name": "Sheet Name Quoting",
        "description": (
            "Ensures all sheet names in verification ranges are properly "
            "quoted with single quotes (e.g., 'Sheet Name'!A1:B2)"
        ),
        "supports_fix": False,
        "supports_flag": True,
    },
    # Spreadsheet Comparison Validators
    {
        "id": "tab_name_consistency",
        "name": "Tab Name Consistency",
        "description": (
            "Ensures tab names referenced in verification ranges exist "
            "with exact casing in both input and output spreadsheets"
        ),
        "supports_fix": False,
        "supports_flag": True,
    },
    {
        "id": "open_ended_ranges",
        "name": "Open-Ended Ranges Detection",
        "description": (
            "Detects unbounded A1 notations in verification ranges that "
            "can cause flaky verification (whole columns, rows, half-bounded ranges)"
        ),
        "supports_fix": False,
        "supports_flag": True,
    },
    {
        "id": "sheet_accessibility",
        "name": "Check Sheet Accessibility",
        "description": "Validates that Google Sheets URLs are accessible",
        "supports_fix": False,
        "supports_flag": True,
    },
    {
        "id": "identical_outside_ranges",
        "name": "Identical Outside Ranges",
        "description": (
            "Ensures input and output spreadsheets are identical except "
            "in specified verification ranges"
        ),
        "supports_fix": False,
        "supports_flag": True,
    },
    # Labeling Aid Validators
    {
        "id": "platform_neutralizer",
        "name": "Neutralize Platform-Specific Language",
        "description": "Detects 'Excel'/'Google Sheets' mentions in prompts and replaces with neutral phrasing.",
        "supports_fix": True,
        "supports_flag": True,
    },
    {
        "id": "attached_files_cleaner",
        "name": "Clean Attached Files Mentions",
        "description": "Detects 'attached file(s)' mentions in prompt text, removes them and adds editor note while preserving grammar.",
        "supports_fix": True,
        "supports_flag": True,
    },
    {
        "id": "empty_invalid_ranges",
        "name": "Empty or Invalid Ranges",
        "description": (
            "Detect invalid or 0-sized ranges pairs with Google sheet urls on the same row."
        ),
        "supports_fix": False,
        "supports_flag": True,
    },
    {
        "id": "csv_to_json_transform",
        "name": "CSV to JSON Transform",
        "description": (
            "Transform the task CSV into JSON with fields: Prompt, Input File, "
            "Output File, Input Excel File, Output Excel File, Verification Field Ranges, "
            "Field Mask, Case Sensitivity, Numeric Rounding, Color matching, "
            "Editor Fixes, Editor Comments, Estimated Task Length. "
            "Detects and fixes malformed A1 range notation (missing quotes/exclamation marks)."
        ),
        "supports_fix": True,
        "supports_flag": True,
    },
    {
        "id": "tab_name_case_collisions",
        "name": "Tab Name Case Collisions",
        "description": (
            "Detect tabs differing only by case (Excel-insensitive); "
            "append (2), (3) suffix; emit mapping"
        ),
        "supports_fix": True,
        "supports_flag": True,
    },
    {
        "id": "spreadsheet_differences",
        "name": "Spreadsheet Differences",
        "description": "Compares two spreadsheets cell-by-cell and reports all differences found",
        "supports_fix": False,
        "supports_flag": True,
    },
    # Formula Validators
    {
        "id": "volatile_formulas",
        "name": "Detect Volatile Formulas and External References",
        "description": (
            "Detects NOW(), TODAY(), RAND(), RANDBETWEEN(), OFFSET(), INDIRECT(), and external references; "
            "suggests deterministic alternatives or pasting values instead."
        ),
        "supports_fix": False,
        "supports_flag": True,
    },
    # Input Validation Validators
    {
        "id": "no_correct_answers",
        "name": "Detect No Correct Answers",
        "description": (
            "Detects when input sheets contain no valid answers by comparing input vs expected output patterns "
            "and flagging template/blank cases with confidence scoring."
        ),
        "supports_fix": False,
        "supports_flag": True,
    },
    {
        "id": "hidden_unicode",
        "name": "Hidden Unicode Detection",
        "description": "Detects non-breaking spaces and hidden Unicode characters and suggests normalization",
        "supports_fix": False,
        "supports_flag": True,
    },
    {
        "id": "whitespace_diff",
        "name": "Leading/Trailing Whitespace Difference Detection",
        "description": "Detects whitespace-only differences between input/output, flags invisible character discrepancies, and suggests normalization",
        "supports_fix": False,
        "supports_flag": True,
    },
    # Cell Value Validation
    {
        "id": "cell_value_validation",
        "name": "Cell Value Validation",
        "description": "Check if expected values match actual values in specified cells, supporting configuration-based expected value lists and handling data type mismatches",
        "supports_fix": True,
        "supports_flag": True,
    },
    # Duplicate and Overlapping Ranges
    {
        "id": "duplicate_overlapping_ranges",
        "name": "Duplicate and Overlapping Ranges",
        "description": "Detects overlapping verification ranges, duplicate range definitions, conflicting range specifications, and suggests range optimization",
        "supports_fix": False,
        "supports_flag": True,
    },
    # Numeric Rounding Rules
    {
        "id": "numeric_rounding",
        "name": "Numeric Rounding Rules",
        "description": "Detects inconsistent number rounding across sheets, validates decimal place consistency, checks for precision loss in calculations, and suggests standardized rounding rules",
        "supports_fix": True,
        "supports_flag": True,
    },
    # Unique ID Properties
    {
        "id": "unique_id_properties",
        "name": "Unique ID Properties",
        "description": "Validates unique identifier fields in field masks, detects duplicates, ensures format consistency, and flags missing/malformed IDs",
        "supports_fix": True,
        "supports_flag": True,
    },
]
