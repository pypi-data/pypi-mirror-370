from typing import Any, Dict, List, Tuple, Union
from pathlib import Path

from urarovite.validators.base import BaseValidator, ValidationResult
from urarovite.core.spreadsheet import SpreadsheetInterface


class HiddenUnicodeValidator(BaseValidator):
    def __init__(self) -> None:
        super().__init__(
            validator_id="hidden_unicode",
            name="Non-Breaking Space and Hidden Unicode Detection",
            description="Detects non-breaking spaces and hidden Unicode "
            "characters and suggests normalization",
        )

    # Using actual unicode codepoints as keys instead of string representations
    HIDDEN_RULES: Dict[int, Tuple[str, str]] = {
        0x00A0: ("NO-BREAK SPACE", "space"),
        0x202F: ("NARROW NO-BREAK SPACE", "space"),
        0x2002: ("EN SPACE", "space"),
        0x2003: ("EM SPACE", "space"),
        0x2004: ("THREE-PER-EM SPACE", "space"),
        0x2005: ("FOUR-PER-EM SPACE", "space"),
        0x2006: ("SIX-PER-EM SPACE", "space"),
        0x2007: ("FIGURE SPACE", "space"),
        0x2008: ("PUNCTUATION SPACE", "space"),
        0x2009: ("THIN SPACE", "space"),
        0x200A: ("HAIR SPACE", "space"),
        0x00AD: ("SOFT HYPHEN", "remove"),
        0x200B: ("ZERO WIDTH SPACE", "remove"),
        0x200C: ("ZERO WIDTH NON-JOINER", "remove"),
        0x200D: ("ZERO WIDTH JOINER", "remove"),
        0x200E: ("LEFT-TO-RIGHT MARK", "remove"),
        0x200F: ("RIGHT-TO-LEFT MARK", "remove"),
        0xFEFF: ("ZERO WIDTH NO-BREAK SPACE", "remove"),
        0x3000: ("IDEOGRAPHIC SPACE", "space"),
    }

    def _normalize(self, value: str) -> Tuple[str, Dict[str, int]]:
        counts: Dict[str, int] = {}
        out: List[str] = []

        for ch in value:
            code_point = ord(ch)
            rule = self.HIDDEN_RULES.get(code_point)

            if rule is None:
                out.append(ch)
                continue

            # Use the hex representation for counting/reporting
            code_str = f"\\u{code_point:04X}"
            counts[code_str] = counts.get(code_str, 0) + 1

            if rule[1] == "space":
                out.append(" ")
            elif rule[1] == "remove":
                continue
            else:
                out.append(ch)

        normalized = "".join(out)
        return normalized, counts

    def validate(
        self,
        spreadsheet_source: Union[str, Path, SpreadsheetInterface],
        mode: str,
        auth_credentials: Dict[str, Any] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Check for and optionally normalize hidden Unicode characters.

        Args:
            spreadsheet_source: Either a Google Sheets URL, Excel file path,
                or SpreadsheetInterface
            mode: Either "fix" (normalize characters) or "flag" (report only)
            auth_credentials: Authentication credentials (required for
                Google Sheets)

        Returns:
            Dict with validation results
        """

        def validation_logic(
            spreadsheet: SpreadsheetInterface, result: ValidationResult, **kwargs
        ) -> None:
            fixes_by_sheet: Dict[str, List[Dict[str, Any]]] = {}

            def process_sheet(
                tab_name: str, data: List[List[Any]], result: ValidationResult
            ) -> None:
                sheet_fixes = []
                # Process each cell in this tab
                for row_idx, row in enumerate(data):
                    for col_idx, cell in enumerate(row):
                        if isinstance(cell, str) and cell:
                            normalized, counts = self._normalize(cell)
                            if counts:
                                cell_ref = self._generate_cell_reference(
                                    row_idx, col_idx, tab_name
                                )
                                message = (
                                    "Found hidden Unicode characters: "
                                    + ", ".join(
                                        f"{code} ({self.HIDDEN_RULES[int(code[2:], 16)][0]})"
                                        for code in counts
                                    )
                                )

                                if mode == "fix":
                                    result.add_detailed_fix(
                                        sheet_name=tab_name,
                                        cell=cell_ref,
                                        message=message,
                                        old_value=cell,
                                        new_value=normalized,
                                    )
                                    sheet_fixes.append(
                                        {
                                            "row": row_idx,
                                            "col": col_idx,
                                            "new_value": normalized,
                                        }
                                    )
                                else:
                                    result.add_detailed_issue(
                                        sheet_name=tab_name,
                                        cell=cell_ref,
                                        message=message,
                                        value=cell,
                                    )

                # Store fixes for this sheet
                if sheet_fixes:
                    fixes_by_sheet[tab_name] = sheet_fixes

            # Process all sheets using the base class helper
            self._process_all_sheets(spreadsheet, process_sheet, result)

            # Apply fixes if in fix mode
            if mode == "fix" and fixes_by_sheet:
                for sheet_name, fixes in fixes_by_sheet.items():
                    # Get original data for this sheet
                    sheet_data = spreadsheet.get_sheet_data(sheet_name)
                    if sheet_data and sheet_data.values:
                        self._apply_fixes_to_sheet(
                            spreadsheet, sheet_name, sheet_data.values, fixes
                        )

                # Save changes (important for Excel files)
                spreadsheet.save()

            # Set a summary log message
            if result.fixes_applied > 0:
                result.set_automated_log(
                    f"Fixed hidden Unicode in {result.fixes_applied} cells."
                )
            elif result.flags_found > 0:
                result.set_automated_log(
                    f"Found hidden Unicode in {result.flags_found} cells."
                )
            else:
                result.set_automated_log("No flags found")

        return self._execute_validation(
            validation_logic, spreadsheet_source, auth_credentials, **kwargs
        )


def run(
    spreadsheet_source: Union[str, Path, SpreadsheetInterface],
    mode: str = "flag",
    auth_credentials: Dict[str, Any] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Backward compatibility function for the hidden unicode validator.

    Args:
        spreadsheet_source: Either a Google Sheets URL, Excel file path,
            or SpreadsheetInterface
        mode: Either "fix" (normalize characters) or "flag" (report only)
        auth_credentials: Authentication credentials (required for
            Google Sheets)

    Returns:
        Dict with validation results
    """
    validator = HiddenUnicodeValidator()
    return validator.validate(spreadsheet_source, mode, auth_credentials, **kwargs)
