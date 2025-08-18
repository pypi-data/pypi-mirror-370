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
        "id": "duplicate_rows",
        "name": "Remove Duplicate Rows",
        "description": "Finds and optionally removes duplicate rows based on all columns",
        "supports_fix": True,
        "supports_flag": True,
    },
    {
        "id": "inconsistent_formatting",
        "name": "Fix Inconsistent Formatting",
        "description": "Standardizes text formatting (case, whitespace, etc.)",
        "supports_fix": True,
        "supports_flag": True,
    },
    {
        "id": "missing_required_fields",
        "name": "Check Required Fields",
        "description": "Validates that required fields are not empty",
        "supports_fix": False,
        "supports_flag": True,
    },
    {
        "id": "tab_names",
        "name": "Fix Tab Names",
        "description": "Validates tab names for illegal characters and Excel length limits (31 chars). Fixes illegal characters and truncates long names with collision-safe suffixes.",
        "supports_fix": True,
        "supports_flag": True,
    },
    # Format Validation
    {
        "id": "invalid_emails",
        "name": "Validate Email Addresses",
        "description": "Checks email format and flags invalid emails",
        "supports_fix": False,
        "supports_flag": True,
    },
    {
        "id": "invalid_phone_numbers",
        "name": "Validate Phone Numbers",
        "description": "Validates phone number formats and consistency",
        "supports_fix": True,
        "supports_flag": True,
    },
    {
        "id": "invalid_dates",
        "name": "Validate Date Formats",
        "description": "Checks and standardizes date formats",
        "supports_fix": True,
        "supports_flag": True,
    },
    {
        "id": "invalid_urls",
        "name": "Validate URLs",
        "description": "Validates URL format and accessibility",
        "supports_fix": False,
        "supports_flag": True,
    },
    {
        "id": "invalid_verification_ranges",
        "name": "Fix Verification Ranges",
        "description": "Validates and fixes malformed A1 notation ranges",
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
    {
        "id": "hidden_unicode",
        "name": "Hidden Unicode Detection",
        "description": "Detects non-breaking spaces and hidden Unicode characters and suggests normalization",
        "supports_fix": False,
        "supports_flag": True,
    },
]
