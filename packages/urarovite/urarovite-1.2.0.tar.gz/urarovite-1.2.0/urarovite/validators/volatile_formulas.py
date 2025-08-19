"""
Validator to detect volatile formulas and external references.

Detects usage of NOW(), TODAY(), RAND(), RANDBETWEEN(), OFFSET(), INDIRECT(), and
external references. Suggests deterministic alternatives or recommends pasting values.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Union
from collections import defaultdict
from pathlib import Path

from urarovite.validators.base import BaseValidator, ValidationResult
from urarovite.core.spreadsheet import SpreadsheetInterface
from urarovite.core.exceptions import ValidationError
from urarovite.utils.sheets import extract_sheet_id, fetch_workbook_with_formulas
from urarovite.utils.sheets import col_index_to_letter


_VOLATILE_FUNCS = [
    "NOW",
    "TODAY",
    "RAND",
    "RANDBETWEEN",
    "OFFSET",
    "INDIRECT",
]

_IMPORT_RANGE_RE = re.compile(r"\bIMPORTRANGE\s*\(", re.IGNORECASE)
_CROSS_TAB_RE = re.compile(r"(^|[^A-Z0-9_'])'?.+?'?![A-Z]+[0-9]+", re.IGNORECASE)


def _cell_ref(row_idx: int, col_idx: int) -> str:
    return f"{col_index_to_letter(col_idx)}{row_idx + 1}"


def _find_flags_in_formula(
    tab: str, r: int, c: int, formula: str
) -> List[Dict[str, Any]]:
    flags: List[Dict[str, Any]] = []

    upper = formula.upper()

    for fn in _VOLATILE_FUNCS:
        if re.search(rf"\b{fn}\s*\(", upper):
            flags.append(
                {
                    "type": "volatile_function",
                    "function": fn,
                    "tab": tab,
                    "cell": _cell_ref(r, c),
                    "formula": formula,
                    "suggestion": _suggestion_for(fn),
                    "severity": _get_severity(fn),
                }
            )

    if _IMPORT_RANGE_RE.search(upper):
        flags.append(
            {
                "type": "external_reference",
                "pattern": "IMPORTRANGE",
                "tab": tab,
                "cell": _cell_ref(r, c),
                "formula": formula,
                "suggestion": "Replace IMPORTRANGE with the values it is referencing",
                "severity": "high",
            }
        )

    if _CROSS_TAB_RE.search(formula):
        flags.append(
            {
                "type": "cross_tab_reference",
                "tab": tab,
                "cell": _cell_ref(r, c),
                "formula": formula,
                "suggestion": "Replace it with values the cross tab address is referencing",
                "severity": "medium",
            }
        )

    return flags


def _suggestion_for(fn: str) -> str:
    suggestions = {
        "NOW": "Use a fixed timestamp or =DATE(YEAR,MONTH,DAY)+TIME(HOUR,MIN,SEC)",
        "TODAY": "Use a fixed date like =DATE(2024,12,15) or manual date entry",
        "RAND": "Generate random values externally and paste as values, or use fixed test data",
        "RANDBETWEEN": "Generate random values externally and paste as values, or use fixed test data",
        "OFFSET": "Replace with direct cell references like A1:B10 instead of OFFSET-based ranges",
        "INDIRECT": "Replace with direct A1 references instead of text-based cell addresses",
    }
    return suggestions.get(fn, "Replace with deterministic alternative or paste values")


def _get_severity(fn: str) -> str:
    """Assign severity levels to different volatile functions"""
    high_impact = ["NOW", "TODAY", "RAND", "RANDBETWEEN"]  # Time-sensitive or random
    medium_impact = ["OFFSET", "INDIRECT"]  # Performance and maintenance flags

    if fn in high_impact:
        return "high"
    elif fn in medium_impact:
        return "medium"
    else:
        return "low"


def _generate_summary_report(flags: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate a comprehensive summary of found flags"""

    # Count by type
    type_counts = defaultdict(int)
    function_counts = defaultdict(int)
    tab_counts = defaultdict(int)
    severity_counts = defaultdict(int)

    for issue in flags:
        type_counts[issue["type"]] += 1
        severity_counts[issue["severity"]] += 1
        tab_counts[issue["tab"]] += 1

        if issue["type"] == "volatile_function":
            function_counts[issue["function"]] += 1

    # Create summary
    summary = {
        "total_flags": len(flags),
        "by_type": dict(type_counts),
        "by_function": dict(function_counts),
        "by_tab": dict(tab_counts),
        "by_severity": dict(severity_counts),
        "tabs_affected": len(tab_counts),
    }

    return summary


def _generate_automated_log(
    flags: List[Dict[str, Any]], summary: Dict[str, Any]
) -> str:
    """Generate detailed automated log showing specific cells with flags"""

    if not flags:
        return "No flags found"

    total = summary["total_flags"]

    # Group flags by tab and type for cleaner reporting
    flags_by_tab = defaultdict(lambda: defaultdict(list))
    for issue in flags:
        tab = issue["tab"]
        issue_type = issue.get("function", issue["type"])
        flags_by_tab[tab][issue_type].append(issue)

    log_parts = [f"Flagged {total} volatile formula flags:"]

    # Show flags by tab with specific cell locations
    for tab_name, tab_flags in flags_by_tab.items():
        tab_parts = []

        for issue_type, issue_list in tab_flags.items():
            # Get cell references for this issue type
            cells = [issue["cell"] for issue in issue_list]

            # Limit cell display to avoid overly long logs
            if len(cells) <= 5:
                cell_display = ", ".join(cells)
            else:
                cell_display = f"{', '.join(cells[:5])} and {len(cells) - 5} more"

            # Create description based on issue type
            if issue_type in _VOLATILE_FUNCS:
                tab_parts.append(f"{issue_type}() in cells {cell_display}")
            elif issue_type == "external_reference":
                tab_parts.append(f"IMPORTRANGE in cells {cell_display}")
            elif issue_type == "cross_tab_reference":
                tab_parts.append(f"Cross-tab references in cells {cell_display}")
            else:
                tab_parts.append(f"{issue_type} in cells {cell_display}")

        # Add tab summary to main log
        tab_summary = f"Tab '{tab_name}': {'; '.join(tab_parts)}"
        log_parts.append(tab_summary)

    # Add action recommendation
    if total <= 10:
        log_parts.append(
            "Action required: Review and replace these formulas with static values or deterministic alternatives"
        )
    else:
        log_parts.append(
            f"Action required: {total} formulas need manual review - consider batch replacement with static values"
        )

    return " | ".join(log_parts)


class VolatileFormulasValidator(BaseValidator):
    def __init__(self) -> None:
        super().__init__(
            validator_id="volatile_formulas",
            name="Detect Volatile Formulas and External References",
            description=(
                "Detect NOW(), TODAY(), RAND(), RANDBETWEEN(), OFFSET(), INDIRECT(), and external references; "
                "suggest deterministic alternatives or paste values"
            ),
        )

    def validate(
        self,
        spreadsheet_source: Union[str, Path, SpreadsheetInterface],
        mode: str,
        auth_credentials: Dict[str, Any] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Detect volatile formulas and external references.

        Args:
            spreadsheet_source: Either a Google Sheets URL, Excel file path,
                or SpreadsheetInterface
            mode: Either "fix" (not applicable) or "flag" (report only)
            auth_credentials: Authentication credentials (required for
                Google Sheets)

        Returns:
            Dict with validation results
        """

        def validation_logic(
            spreadsheet: SpreadsheetInterface, result: ValidationResult, **kwargs
        ) -> None:
            # For Google Sheets, we need to use the raw API to get formulas
            # This validator requires special handling since formulas aren't
            # exposed through the standard spreadsheet interface

            # Extract sheet ID from spreadsheet source
            if (
                isinstance(spreadsheet_source, str)
                and "docs.google.com" in spreadsheet_source
            ):
                try:
                    sheet_id = self._extract_sheet_id_from_url(spreadsheet_source)
                    sheets_service = self._create_sheets_service(auth_credentials)
                except ValidationError as e:
                    result.add_error(str(e))
                    return

                # Fetch workbook with formulas using the utility function
                try:
                    workbook = fetch_workbook_with_formulas(sheets_service, sheet_id)
                except Exception as e:
                    result.add_error(f"Failed to fetch workbook formulas: {str(e)}")
                    result.set_automated_log(
                        f"Failed to fetch workbook formulas: {str(e)}"
                    )
                    return

                flags: List[Dict[str, Any]] = []

                # Scan all sheets for volatile formulas
                for sheet in workbook.get("sheets", []):
                    title = sheet.get("properties", {}).get("title", "")
                    for grid in sheet.get("data", []) or []:
                        for r_idx, row in enumerate(grid.get("rowData", []) or []):
                            for c_idx, cell in enumerate(row.get("values", []) or []):
                                uev = (cell.get("userEnteredValue") or {}).get(
                                    "formulaValue"
                                )
                                if uev:
                                    flags.extend(
                                        _find_flags_in_formula(
                                            title, r_idx, c_idx, str(uev)
                                        )
                                    )

                # Process results
                if flags:
                    summary = _generate_summary_report(flags)
                    result.add_issue(len(flags))
                    result.details.update(
                        {
                            "flags": flags,
                            "summary": summary,
                            "validation_mode": mode,
                            "spreadsheet_scanned": True,
                        }
                    )
                    automated_log = _generate_automated_log(flags, summary)
                    result.set_automated_log(automated_log)
                else:
                    result.set_automated_log("No flags found")
                    result.details.update(
                        {
                            "flags": [],
                            "summary": {"total_flags": 0, "spreadsheet_clean": True},
                            "validation_mode": mode,
                            "spreadsheet_scanned": True,
                        }
                    )
            else:
                # Use generic utility that works with both Google Sheets and Excel
                try:
                    from urarovite.utils.generic_spreadsheet import (
                        get_spreadsheet_formulas,
                    )

                    workbook = get_spreadsheet_formulas(
                        spreadsheet_source, auth_credentials
                    )
                except Exception as e:
                    result.add_error(f"Failed to fetch workbook formulas: {str(e)}")
                    result.set_automated_log(
                        f"Failed to fetch workbook formulas: {str(e)}"
                    )
                    result.details.update(
                        {
                            "validation_failed": True,
                            "validation_mode": mode,
                            "spreadsheet_scanned": False,
                        }
                    )
                    return

                if not workbook:
                    # No formulas found
                    result.set_automated_log("No formulas found in spreadsheet")
                    result.details.update(
                        {
                            "flags": [],
                            "summary": {
                                "total_flags": 0,
                                "by_type": {},
                                "by_severity": {},
                            },
                            "validation_mode": mode,
                            "spreadsheet_scanned": True,
                        }
                    )
                    return

                flags: List[Dict[str, Any]] = []

                # Scan all sheets for volatile formulas
                for tab_name, formulas in workbook.items():
                    for cell_ref, formula in formulas.items():
                        # Extract row and column from cell reference (e.g., "A1" -> 0, 0)
                        col_match = re.match(r"([A-Z]+)(\d+)", cell_ref)
                        if col_match:
                            col_letters, row_num = col_match.groups()
                            row_idx = int(row_num) - 1
                            col_idx = (
                                sum(
                                    (ord(c) - ord("A") + 1) * (26**i)
                                    for i, c in enumerate(reversed(col_letters))
                                )
                                - 1
                            )

                            cell_flags = _find_flags_in_formula(
                                tab_name, row_idx, col_idx, formula
                            )
                            flags.extend(cell_flags)

                # Generate summary and automated log
                summary = _generate_summary_report(flags)
                automated_log = _generate_automated_log(flags, summary)

                # Store results
                result.add_issue(len(flags))
                result.set_automated_log(automated_log)
                result.details.update(
                    {
                        "flags": flags,
                        "summary": summary,
                        "validation_mode": mode,
                        "spreadsheet_scanned": True,
                    }
                )

        return self._execute_validation(
            validation_logic, spreadsheet_source, auth_credentials, **kwargs
        )


def run(
    spreadsheet_source: Union[str, Path, SpreadsheetInterface],
    mode: str = "flag",
    auth_credentials: Dict[str, Any] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Backward compatibility function for the volatile formulas validator.

    Args:
        spreadsheet_source: Either a Google Sheets URL, Excel file path,
            or SpreadsheetInterface
        mode: Either "fix" (not applicable) or "flag" (report only)
        auth_credentials: Authentication credentials (required for
            Google Sheets)

    Returns:
        Dict with validation results
    """
    validator = VolatileFormulasValidator()
    return validator.validate(spreadsheet_source, mode, auth_credentials, **kwargs)
