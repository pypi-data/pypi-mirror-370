"""Whitespace difference validator for detecting leading/trailing whitespace discrepancies.

This validator identifies whitespace-only differences between input and output
spreadsheets, flags invisible character discrepancies, and suggests normalization.
"""

from typing import Any, Dict, List, Union, Tuple
from pathlib import Path
import re

from urarovite.validators.base import BaseValidator, ValidationResult
from urarovite.core.spreadsheet import SpreadsheetInterface


class WhitespaceDiffValidator(BaseValidator):
    """Validator for detecting whitespace differences between input/output spreadsheets."""

    def __init__(self) -> None:
        super().__init__(
            validator_id="whitespace_diff",
            name="Leading/Trailing Whitespace Difference Detection",
            description="Detects whitespace-only differences between input/output, "
            "flags invisible character discrepancies, and suggests normalization",
        )

    # Common whitespace characters and their representations
    WHITESPACE_CHARS: Dict[str, Tuple[str, str]] = {
        " ": ("SPACE", "space"),
        "\t": ("TAB", "tab"),
        "\n": ("NEWLINE", "newline"),
        "\r": ("CARRIAGE_RETURN", "carriage_return"),
        "\f": ("FORM_FEED", "form_feed"),
        "\v": ("VERTICAL_TAB", "vertical_tab"),
        "\u00a0": ("NO_BREAK_SPACE", "no_break_space"),
        "\u2000": ("EN_QUAD", "en_quad"),
        "\u2001": ("EM_QUAD", "em_quad"),
        "\u2002": ("EN_SPACE", "en_space"),
        "\u2003": ("EM_SPACE", "em_space"),
        "\u2004": ("THREE_PER_EM_SPACE", "three_per_em_space"),
        "\u2005": ("FOUR_PER_EM_SPACE", "four_per_em_space"),
        "\u2006": ("SIX_PER_EM_SPACE", "six_per_em_space"),
        "\u2007": ("FIGURE_SPACE", "figure_space"),
        "\u2008": ("PUNCTUATION_SPACE", "punctuation_space"),
        "\u2009": ("THIN_SPACE", "thin_space"),
        "\u200a": ("HAIR_SPACE", "hair_space"),
        "\u200b": ("ZERO_WIDTH_SPACE", "zero_width_space"),
        "\u200c": ("ZERO_WIDTH_NON_JOINER", "zero_width_non_joiner"),
        "\u200d": ("ZERO_WIDTH_JOINER", "zero_width_joiner"),
        "\u200e": ("LEFT_TO_RIGHT_MARK", "left_to_right_mark"),
        "\u200f": ("RIGHT_TO_LEFT_MARK", "right_to_left_mark"),
        "\u2028": ("LINE_SEPARATOR", "line_separator"),
        "\u2029": ("PARAGRAPH_SEPARATOR", "paragraph_separator"),
        "\u202f": ("NARROW_NO_BREAK_SPACE", "narrow_no_break_space"),
        "\u205f": ("MEDIUM_MATHEMATICAL_SPACE", "medium_mathematical_space"),
        "\u2060": ("WORD_JOINER", "word_joiner"),
        "\u3000": ("IDEOGRAPHIC_SPACE", "ideographic_space"),
        "\ufeff": ("ZERO_WIDTH_NO_BREAK_SPACE", "zero_width_no_break_space"),
    }

    def _analyze_whitespace(self, value: str) -> Dict[str, Any]:
        """Analyze whitespace in a string value.

        Args:
            value: String value to analyze

        Returns:
            Dictionary with whitespace analysis
        """
        if not isinstance(value, str):
            return {}

        analysis = {
            "leading_whitespace": "",
            "trailing_whitespace": "",
            "leading_chars": [],
            "trailing_chars": [],
            "has_leading": False,
            "has_trailing": False,
            "normalized": value.strip(),
            "original_length": len(value),
            "normalized_length": len(value.strip()),
        }

        # Find leading whitespace
        leading_match = re.match(r"^(\s+)", value)
        if leading_match:
            analysis["leading_whitespace"] = leading_match.group(1)
            analysis["has_leading"] = True
            analysis["leading_chars"] = self._identify_whitespace_chars(
                leading_match.group(1)
            )

        # Find trailing whitespace
        trailing_match = re.search(r"(\s+)$", value)
        if trailing_match:
            analysis["trailing_whitespace"] = trailing_match.group(1)
            analysis["has_trailing"] = True
            analysis["trailing_chars"] = self._identify_whitespace_chars(
                trailing_match.group(1)
            )

        return analysis

    def _identify_whitespace_chars(self, whitespace: str) -> List[Dict[str, Any]]:
        """Identify specific whitespace characters in a string.

        Args:
            whitespace: String containing only whitespace characters

        Returns:
            List of dictionaries describing each whitespace character
        """
        chars = []
        for char in whitespace:
            if char in self.WHITESPACE_CHARS:
                name, code = self.WHITESPACE_CHARS[char]
                chars.append(
                    {
                        "char": char,
                        "name": name,
                        "code": code,
                        "unicode": f"\\u{ord(char):04X}",
                        "description": f"{name} (\\u{ord(char):04X})",
                    }
                )
            else:
                # Fallback for unknown whitespace characters
                chars.append(
                    {
                        "char": char,
                        "name": "UNKNOWN_WHITESPACE",
                        "code": "unknown",
                        "unicode": f"\\u{ord(char):04X}",
                        "description": f"Unknown whitespace (\\u{ord(char):04X})",
                    }
                )
        return chars

    def _compare_values(self, input_value: Any, output_value: Any) -> Dict[str, Any]:
        """Compare input and output values for whitespace differences.

        Args:
            input_value: Value from input spreadsheet
            output_value: Value from output spreadsheet

        Returns:
            Dictionary describing the differences found
        """
        # Convert to strings for comparison
        input_str = str(input_value) if input_value is not None else ""
        output_str = str(output_value) if output_value is not None else ""

        # Analyze whitespace in both values
        input_analysis = self._analyze_whitespace(input_str)
        output_analysis = self._analyze_whitespace(output_str)

        # Check if values are identical after normalization
        input_normalized = input_analysis.get("normalized", "")
        output_normalized = output_analysis.get("normalized", "")

        differences = {
            "input_analysis": input_analysis,
            "output_analysis": output_analysis,
            "has_differences": False,
            "differences": [],
            "suggested_fix": None,
        }

        # Check for content differences (ignoring whitespace)
        if input_normalized != output_normalized:
            differences["differences"].append(
                {
                    "type": "content_difference",
                    "description": "Values differ in content, not just whitespace",
                    "input_normalized": input_normalized,
                    "output_normalized": output_normalized,
                }
            )
            differences["has_differences"] = True
            return differences

        # Check for whitespace-only differences
        if input_analysis.get("has_leading") != output_analysis.get(
            "has_leading"
        ) or input_analysis.get("has_trailing") != output_analysis.get("has_trailing"):
            differences["differences"].append(
                {
                    "type": "whitespace_difference",
                    "description": "Values differ only in leading/trailing whitespace",
                    "input_leading": input_analysis.get("has_leading", False),
                    "input_trailing": input_analysis.get("has_trailing", False),
                    "output_leading": output_analysis.get("has_leading", False),
                    "output_trailing": output_analysis.get("has_trailing", False),
                }
            )
            differences["has_differences"] = True

        # Check for different types of whitespace characters
        if input_analysis.get("leading_chars") != output_analysis.get("leading_chars"):
            differences["differences"].append(
                {
                    "type": "leading_whitespace_type",
                    "description": "Different types of leading whitespace characters",
                    "input_chars": input_analysis.get("leading_chars", []),
                    "output_chars": output_analysis.get("leading_chars", []),
                }
            )
            differences["has_differences"] = True

        if input_analysis.get("trailing_chars") != output_analysis.get(
            "trailing_chars"
        ):
            differences["differences"].append(
                {
                    "type": "trailing_whitespace_type",
                    "description": "Different types of trailing whitespace characters",
                    "input_chars": input_analysis.get("trailing_chars", []),
                    "output_chars": output_analysis.get("trailing_chars", []),
                }
            )
            differences["has_differences"] = True

        # Suggest normalization if there are differences
        if differences["has_differences"]:
            differences["suggested_fix"] = {
                "action": "normalize",
                "description": "Normalize whitespace by trimming leading/trailing whitespace",
                "input_normalized": input_normalized,
                "output_normalized": output_normalized,
            }

        return differences

    def validate(
        self,
        spreadsheet_source: Union[str, Path, SpreadsheetInterface],
        mode: str,
        auth_credentials: Dict[str, Any] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Check for whitespace differences between input and output spreadsheets.

        Args:
            spreadsheet_source: Either a Google Sheets URL, Excel file path,
                or SpreadsheetInterface
            mode: Either "fix" (normalize whitespace) or "flag" (report only)
            auth_credentials: Authentication credentials (required for
                Google Sheets)

        Returns:
            Dict with validation results
        """

        def validation_logic(
            spreadsheet: SpreadsheetInterface, result: ValidationResult, **kwargs
        ) -> None:
            fixes_by_sheet = {}

            # Get metadata to check if this is a comparison scenario
            try:
                metadata = spreadsheet.get_metadata()
                sheet_names = metadata.sheet_names

                # Look for input/output sheet pairs
                input_sheets = [name for name in sheet_names if "input" in name.lower()]
                output_sheets = [
                    name for name in sheet_names if "output" in name.lower()
                ]

                if not input_sheets or not output_sheets:
                    # Single spreadsheet mode - check for whitespace flags within sheets
                    self._check_single_spreadsheet_whitespace(
                        spreadsheet, result, mode, fixes_by_sheet
                    )
                else:
                    # Comparison mode - compare input vs output sheets
                    self._check_input_output_comparison(
                        spreadsheet,
                        result,
                        mode,
                        input_sheets,
                        output_sheets,
                        fixes_by_sheet,
                    )

            except Exception as e:
                result.add_error(f"Failed to analyze spreadsheet structure: {str(e)}")
                return

            # Apply fixes if in fix mode
            if mode == "fix" and fixes_by_sheet:
                for sheet_name, fixes in fixes_by_sheet.items():
                    sheet_data = spreadsheet.get_sheet_data(sheet_name)
                    if sheet_data and sheet_data.values:
                        self._apply_fixes_to_sheet(
                            spreadsheet, sheet_name, sheet_data.values, fixes
                        )

                # Save changes
                spreadsheet.save()

        return self._execute_validation(
            validation_logic, spreadsheet_source, auth_credentials, **kwargs
        )

    def _check_single_spreadsheet_whitespace(
        self,
        spreadsheet: SpreadsheetInterface,
        result: ValidationResult,
        mode: str,
        fixes_by_sheet: Dict[str, List[Dict[str, Any]]],
    ) -> None:
        """Check for whitespace flags within a single spreadsheet.

        Args:
            spreadsheet: SpreadsheetInterface instance
            result: ValidationResult to accumulate results
            mode: Validation mode
            fixes_by_sheet: Dictionary to store fixes by sheet
        """

        def process_sheet(
            tab_name: str, data: List[List[Any]], result: ValidationResult
        ) -> None:
            sheet_fixes = []
            sheet_flags = 0

            for row_idx, row in enumerate(data):
                for col_idx, cell in enumerate(row):
                    if isinstance(cell, str) and cell:
                        analysis = self._analyze_whitespace(cell)

                        if analysis.get("has_leading") or analysis.get("has_trailing"):
                            self._generate_cell_reference(row_idx, col_idx, tab_name)

                            if mode == "fix":
                                sheet_fixes.append(
                                    {
                                        "row": row_idx,
                                        "col": col_idx,
                                        "new_value": analysis.get("normalized", ""),
                                    }
                                )
                                result.add_fix(1)
                            else:
                                result.add_issue(1)

                            sheet_flags += 1

            if sheet_fixes:
                fixes_by_sheet[tab_name] = sheet_fixes

        self._process_all_sheets(spreadsheet, process_sheet, result)

    def _check_input_output_comparison(
        self,
        spreadsheet: SpreadsheetInterface,
        result: ValidationResult,
        mode: str,
        input_sheets: List[str],
        output_sheets: List[str],
        fixes_by_sheet: Dict[str, List[Dict[str, Any]]],
    ) -> None:
        """Compare input and output sheets for whitespace differences.

        Args:
            spreadsheet: SpreadsheetInterface instance
            result: ValidationResult to accumulate results
            mode: Validation mode
            input_sheets: List of input sheet names
            output_sheets: List of output sheet names
            fixes_by_sheet: Dictionary to store fixes by sheet
        """
        # For now, compare the first input and output sheets
        if input_sheets and output_sheets:
            input_sheet = input_sheets[0]
            output_sheet = output_sheets[0]

            try:
                input_data = spreadsheet.get_sheet_data(input_sheet)
                output_data = spreadsheet.get_sheet_data(output_sheet)

                if (
                    input_data
                    and output_data
                    and input_data.values
                    and output_data.values
                ):
                    self._compare_sheet_data(
                        spreadsheet,
                        result,
                        mode,
                        input_sheet,
                        output_sheet,
                        input_data.values,
                        output_data.values,
                        fixes_by_sheet,
                    )

            except Exception as e:
                result.add_error(f"Failed to compare sheets: {str(e)}")

    def _compare_sheet_data(
        self,
        spreadsheet: SpreadsheetInterface,
        result: ValidationResult,
        mode: str,
        input_sheet: str,
        output_sheet: str,
        input_data: List[List[Any]],
        output_data: List[List[Any]],
        fixes_by_sheet: Dict[str, List[Dict[str, Any]]],
    ) -> None:
        """Compare data between input and output sheets.

        Args:
            spreadsheet: SpreadsheetInterface instance
            result: ValidationResult to accumulate results
            mode: Validation mode
            input_sheet: Name of input sheet
            output_sheet: Name of output sheet
            input_data: Input sheet data
            output_data: Output sheet data
            fixes_by_sheet: Dictionary to store fixes by sheet
        """
        input_fixes = []
        output_fixes = []
        flags_found = 0

        # Compare cells up to the minimum dimensions
        max_rows = min(len(input_data), len(output_data))
        max_cols = min(
            max(len(row) for row in input_data) if input_data else 0,
            max(len(row) for row in output_data) if output_data else 0,
        )

        for row_idx in range(max_rows):
            for col_idx in range(max_cols):
                input_value = (
                    input_data[row_idx][col_idx]
                    if col_idx < len(input_data[row_idx])
                    else None
                )
                output_value = (
                    output_data[row_idx][col_idx]
                    if col_idx < len(output_data[row_idx])
                    else None
                )

                # Compare values for whitespace differences
                differences = self._compare_values(input_value, output_value)

                if differences.get("has_differences"):
                    flags_found += 1

                    if mode == "fix" and differences.get("suggested_fix"):
                        # Apply normalization to output sheet
                        output_fixes.append(
                            {
                                "row": row_idx,
                                "col": col_idx,
                                "new_value": differences["suggested_fix"][
                                    "output_normalized"
                                ],
                            }
                        )

                        result.add_fix(1)
                    else:
                        result.add_issue(1)

        # Store fixes
        if input_fixes:
            fixes_by_sheet[input_sheet] = input_fixes
        if output_fixes:
            fixes_by_sheet[output_sheet] = output_fixes


def run(
    spreadsheet_source: Union[str, Path, SpreadsheetInterface],
    mode: str = "flag",
    auth_credentials: Dict[str, Any] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Backward compatibility function for the whitespace diff validator.

    Args:
        spreadsheet_source: Either a Google Sheets URL, Excel file path,
            or SpreadsheetInterface
        mode: Either "fix" (normalize whitespace) or "flag" (report only)
        auth_credentials: Authentication credentials (required for
            Google Sheets)

    Returns:
        Dict with validation results
    """
    validator = WhitespaceDiffValidator()
    return validator.validate(spreadsheet_source, mode, auth_credentials, **kwargs)
