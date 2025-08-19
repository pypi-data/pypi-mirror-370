"""Case sensitivity hint validator for detecting potential case-related validation flags.

This validator analyzes spreadsheet data to identify patterns that suggest
case sensitivity might be important, and provides hints for prompt requirements.
"""

import re
from typing import Any, Dict, List, Set, Union
from pathlib import Path

from urarovite.validators.base import BaseValidator, ValidationResult
from urarovite.core.exceptions import ValidationError
from urarovite.core.spreadsheet import SpreadsheetInterface


class CaseSensitivityHintValidator(BaseValidator):
    """Validator for detecting potential case sensitivity requirements."""

    def __init__(self) -> None:
        super().__init__(
            validator_id="case_sensitivity_hint",
            name="Case Sensitivity Hint",
            description=(
                "Detects when case differences might be significant and suggests "
                "case-sensitivity requirements in prompts. Flags potential case-related "
                "validation flags."
            ),
        )

    def validate(
        self,
        spreadsheet_source: Union[str, Path, SpreadsheetInterface],
        mode: str,
        auth_credentials: Dict[str, Any] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Analyze spreadsheet for case sensitivity patterns.

        Args:
            spreadsheet_source: Either a Google Sheets URL, Excel file path,
                or SpreadsheetInterface
            mode: Either "fix" (add hints) or "flag" (report only)
            auth_credentials: Authentication credentials (required for Google Sheets)

        Returns:
            Dict with validation results including case sensitivity hints
        """

        def validation_logic(
            spreadsheet: SpreadsheetInterface, result: ValidationResult, **kwargs
        ) -> None:
            flags = []
            hints_by_sheet = {}

            def process_sheet(
                tab_name: str, data: List[List[Any]], result: ValidationResult
            ) -> None:
                """Process a single sheet for case sensitivity patterns."""
                sheet_hints = []
                sheet_flags = []

                # Analyze column headers for case patterns
                if data and len(data) > 0:
                    header_row = data[0]
                    header_patterns = self._analyze_header_case_patterns(header_row)

                    if header_patterns:
                        sheet_hints.extend(header_patterns)

                # Analyze data for case sensitivity indicators
                data_patterns = self._analyze_data_case_patterns(data)
                if data_patterns:
                    sheet_hints.extend(data_patterns)

                # Check for mixed case in similar values
                mixed_case_flags = self._detect_mixed_case_values(data)
                if mixed_case_flags:
                    sheet_flags.extend(mixed_case_flags)

                # Check for case-sensitive identifiers (IDs, codes, etc.)
                identifier_patterns = self._detect_case_sensitive_identifiers(data)
                if identifier_patterns:
                    sheet_hints.extend(identifier_patterns)

                # Check for case-sensitive categories or labels
                category_patterns = self._detect_case_sensitive_categories(data)
                if category_patterns:
                    sheet_hints.extend(category_patterns)

                if sheet_hints:
                    hints_by_sheet[tab_name] = sheet_hints

                if sheet_flags:
                    flags.extend(sheet_flags)

            # Process all sheets using abstraction layer
            self._process_all_sheets(spreadsheet, process_sheet, result)

            # Apply hints if in fix mode
            if mode == "fix" and hints_by_sheet:
                self._apply_case_sensitivity_hints(spreadsheet, hints_by_sheet, result)
                spreadsheet.save()

                total_fixes = sum(len(hints) for hints in hints_by_sheet.values())
                result.set_automated_log(
                    f"Applied {total_fixes} case sensitivity fixes"
                )
            else:
                # Flag mode - add detailed issue reporting
                for sheet_name, hints in hints_by_sheet.items():
                    for hint in hints:
                        self._report_case_sensitivity_issue(result, sheet_name, hint)

                for issue in flags:
                    # Get sheet name from cell reference
                    sheet_name = ""  # Default if can't parse
                    if "!" in issue.get("cell_ref", ""):
                        sheet_name = issue["cell_ref"].split("!")[0]

                    result.add_detailed_issue(
                        sheet_name=sheet_name,
                        cell=issue.get("cell_ref", ""),
                        message=f"{issue['type'].replace('_', ' ').title()}: {issue['suggestion']}",
                        value=issue.get("value", ""),
                    )

                total_flags = sum(
                    len(hints) for hints in hints_by_sheet.values()
                ) + len(flags)
                if total_flags > 0:
                    result.set_automated_log(
                        f"Found {total_flags} case sensitivity patterns: "
                        f"{sum(len(hints) for hints in hints_by_sheet.values())} hints and "
                        f"{len(flags)} flags"
                    )
                else:
                    result.set_automated_log("No case sensitivity patterns detected")

            # Add detailed results
            result.details["case_sensitivity_hints"] = hints_by_sheet
            result.details["case_related_flags"] = flags

        return self._execute_validation(
            validation_logic, spreadsheet_source, auth_credentials, **kwargs
        )

    def _report_case_sensitivity_issue(
        self, result: ValidationResult, sheet_name: str, hint: Dict[str, Any]
    ) -> None:
        """Report a case sensitivity issue using detailed reporting."""
        hint_type = hint.get("type", "")

        if hint_type == "mixed_case_header":
            result.add_detailed_issue(
                sheet_name=sheet_name,
                cell=hint.get("cell_ref", ""),
                message=f"Mixed case header '{hint.get('header', '')}' - {hint.get('suggestion', '')}",
                value=hint.get("header", ""),
            )
        elif hint_type == "acronym_header":
            result.add_detailed_issue(
                sheet_name=sheet_name,
                cell=hint.get("cell_ref", ""),
                message=f"Acronym header '{hint.get('header', '')}' - {hint.get('suggestion', '')}",
                value=hint.get("header", ""),
            )
        elif hint_type == "case_variations":
            examples_str = ", ".join(hint.get("examples", [])[:3])
            result.add_detailed_issue(
                sheet_name=sheet_name,
                cell=examples_str,
                message=f"Case variations for '{hint.get('normalized_value', '')}' - {hint.get('suggestion', '')}",
                value=str(hint.get("variations", [])),
            )
        elif hint_type == "id_pattern":
            examples_str = ", ".join(hint.get("examples", [])[:3])
            result.add_detailed_issue(
                sheet_name=sheet_name,
                cell=examples_str,
                message=f"ID pattern detected - {hint.get('suggestion', '')}",
                value=hint.get("pattern", ""),
            )
        elif hint_type in ["case_sensitive_identifiers", "case_sensitive_categories"]:
            result.add_detailed_issue(
                sheet_name=sheet_name,
                cell=f"Column {hint.get('column', 0) + 1}",
                message=f"{hint_type.replace('_', ' ').title()} - {hint.get('suggestion', '')}",
                value=str(hint.get("examples", [])[:3]),
            )
        else:
            # Generic handling
            result.add_detailed_issue(
                sheet_name=sheet_name,
                cell="",
                message=hint.get(
                    "suggestion", f"Case sensitivity pattern detected: {hint_type}"
                ),
                value=str(hint),
            )

    def _analyze_header_case_patterns(
        self, header_row: List[Any]
    ) -> List[Dict[str, Any]]:
        """Analyze column headers for case sensitivity patterns."""
        hints = []

        for col_idx, header in enumerate(header_row):
            if not isinstance(header, str):
                continue

            # Check for mixed case in headers
            if header != header.lower() and header != header.upper():
                hints.append(
                    {
                        "type": "mixed_case_header",
                        "column": col_idx,
                        "header": header,
                        "suggestion": "Consider standardizing header case for consistency",
                        "cell_ref": self._generate_cell_reference(0, col_idx, "Sheet1"),
                    }
                )

            # Check for acronyms or abbreviations
            if re.match(r"^[A-Z]{2,}$", header):
                hints.append(
                    {
                        "type": "acronym_header",
                        "column": col_idx,
                        "header": header,
                        "suggestion": "Acronyms suggest case-sensitive identifiers",
                        "cell_ref": self._generate_cell_reference(0, col_idx, "Sheet1"),
                    }
                )

        return hints

    def _analyze_data_case_patterns(
        self, data: List[List[Any]]
    ) -> List[Dict[str, Any]]:
        """Analyze data for case sensitivity indicators."""
        hints = []

        if len(data) < 2:  # Need at least header + one data row
            return hints

        # Analyze each column for case patterns
        for col_idx in range(len(data[0])):
            column_values = []
            for row_idx in range(1, len(data)):  # Skip header row
                if col_idx < len(data[row_idx]):
                    cell_value = data[row_idx][col_idx]
                    if isinstance(cell_value, str) and cell_value.strip():
                        column_values.append((row_idx, cell_value))

            if not column_values:
                continue

            # Check for mixed case patterns
            case_patterns = self._analyze_column_case_patterns(col_idx, column_values)
            if case_patterns:
                hints.extend(case_patterns)

        return hints

    def _analyze_column_case_patterns(
        self, col_idx: int, column_values: List[tuple[int, str]]
    ) -> List[Dict[str, Any]]:
        """Analyze case patterns in a specific column."""
        hints = []

        # Check for mixed case in similar values
        value_variations = {}
        for row_idx, value in column_values:
            normalized = value.lower().strip()
            if normalized not in value_variations:
                value_variations[normalized] = []
            value_variations[normalized].append((row_idx, value))

        # Look for case variations of the same value
        for normalized, variations in value_variations.items():
            if len(variations) > 1:
                unique_cases = set(variation[1] for variation in variations)
                if len(unique_cases) > 1:
                    hints.append(
                        {
                            "type": "case_variations",
                            "column": col_idx,
                            "normalized_value": normalized,
                            "variations": list(unique_cases),
                            "suggestion": "Multiple case variations detected - consider case sensitivity requirements",
                            "examples": [
                                self._generate_cell_reference(
                                    row_idx, col_idx, "Sheet1"
                                )
                                for row_idx, _ in variations[:3]
                            ],  # Show first 3 examples
                        }
                    )

        # Check for ID-like patterns
        id_patterns = self._detect_id_patterns(col_idx, column_values)
        if id_patterns:
            hints.extend(id_patterns)

        return hints

    def _detect_id_patterns(
        self, col_idx: int, column_values: List[tuple[int, str]]
    ) -> List[Dict[str, Any]]:
        """Detect ID-like patterns that are typically case-sensitive."""
        hints = []

        # Common ID patterns
        id_patterns = [
            r"^[A-Z0-9]{6,}$",  # Alphanumeric codes (6+ chars)
            r"^[A-Z]{2,}[0-9]{2,}$",  # Letters + numbers
            r"^[A-Z]{3,}$",  # All caps (3+ chars)
            r"^[A-Z][a-z]+[0-9]+$",  # PascalCase + numbers
        ]

        for pattern in id_patterns:
            matching_values = []
            for row_idx, value in column_values:
                if re.match(pattern, value):
                    matching_values.append((row_idx, value))

            if len(matching_values) >= 3:  # Need multiple examples to suggest pattern
                hints.append(
                    {
                        "type": "id_pattern",
                        "column": col_idx,
                        "pattern": pattern,
                        "suggestion": "ID-like pattern detected - case sensitivity likely important",
                        "examples": [
                            self._generate_cell_reference(row_idx, col_idx, "Sheet1")
                            for row_idx, _ in matching_values[:3]
                        ],
                    }
                )
                break  # Only report one pattern per column

        return hints

    def _detect_mixed_case_values(self, data: List[List[Any]]) -> List[Dict[str, Any]]:
        """Detect mixed case values that might cause validation flags."""
        flags = []

        if len(data) < 2:
            return flags

        for row_idx in range(1, len(data)):  # Skip header
            for col_idx, cell_value in enumerate(data[row_idx]):
                if not isinstance(cell_value, str) or not cell_value.strip():
                    continue

                # Check for inconsistent case in single values
                if (
                    cell_value != cell_value.lower()
                    and cell_value != cell_value.upper()
                    and not cell_value.istitle()
                ):
                    # Skip if it's a proper noun or title case
                    if not self._is_likely_proper_noun(cell_value):
                        flags.append(
                            {
                                "type": "inconsistent_case",
                                "cell_ref": self._generate_cell_reference(
                                    row_idx, col_idx, "Sheet1"
                                ),
                                "value": cell_value,
                                "suggestion": "Inconsistent case might cause validation flags",
                            }
                        )

        return flags

    def _is_likely_proper_noun(self, value: str) -> bool:
        """Check if a value is likely a proper noun (should have mixed case)."""
        # Common proper noun patterns
        proper_noun_patterns = [
            r"^[A-Z][a-z]*$",  # Single word, title case (allowing single letters like O)
            r"^[A-Z][a-z]*\s+[A-Z][a-z]+$",  # Two words, both title case
            r"^[A-Z][a-z]*-[A-Z][a-z]+$",  # Hyphenated, both title case
            r"^[A-Z][a-z]*\'[a-zA-Z]+$",  # Apostrophe pattern like O'Connor
        ]

        return any(re.match(pattern, value) for pattern in proper_noun_patterns)

    def _detect_case_sensitive_identifiers(
        self, data: List[List[Any]]
    ) -> List[Dict[str, Any]]:
        """Detect columns that likely contain case-sensitive identifiers."""
        hints = []

        if len(data) < 2:
            return hints

        for col_idx in range(len(data[0])):
            # Sample values from the column
            sample_values = []
            for row_idx in range(1, min(len(data), 11)):  # Check first 10 rows
                if col_idx < len(data[row_idx]):
                    cell_value = data[row_idx][col_idx]
                    if isinstance(cell_value, str) and cell_value.strip():
                        sample_values.append(cell_value)

            if len(sample_values) < 3:
                continue

            # Check for characteristics of case-sensitive identifiers
            if self._is_likely_case_sensitive_column(sample_values):
                hints.append(
                    {
                        "type": "case_sensitive_identifiers",
                        "column": col_idx,
                        "header": data[0][col_idx]
                        if col_idx < len(data[0])
                        else f"Column {col_idx + 1}",
                        "suggestion": "Column contains case-sensitive identifiers - maintain exact case",
                        "examples": sample_values[:3],
                    }
                )

        return hints

    def _is_likely_case_sensitive_column(self, values: List[str]) -> bool:
        """Determine if a column likely contains case-sensitive identifiers."""
        if not values:
            return False

        # Check for alphanumeric patterns
        has_alphanumeric = all(re.match(r"^[A-Za-z0-9_-]+$", v) for v in values)

        # Check for consistent length patterns (common in IDs)
        lengths = [len(v) for v in values]
        consistent_length = len(set(lengths)) <= 1  # IDs should have consistent length

        # Check for no spaces (typical for identifiers)
        no_spaces = all(" " not in v for v in values)

        return has_alphanumeric and consistent_length and no_spaces

    def _detect_case_sensitive_categories(
        self, data: List[List[Any]]
    ) -> List[Dict[str, Any]]:
        """Detect columns that likely contain case-sensitive categories or labels."""
        hints = []

        if len(data) < 2:
            return hints

        for col_idx in range(len(data[0])):
            # Sample values from the column
            sample_values = []
            for row_idx in range(1, min(len(data), 21)):  # Check first 20 rows
                if col_idx < len(data[row_idx]):
                    cell_value = data[row_idx][col_idx]
                    if isinstance(cell_value, str) and cell_value.strip():
                        sample_values.append(cell_value)

            if len(sample_values) < 4:
                continue

            # Check for characteristics of categorical data
            if self._is_likely_categorical_column(sample_values):
                hints.append(
                    {
                        "type": "case_sensitive_categories",
                        "column": col_idx,
                        "header": data[0][col_idx]
                        if col_idx < len(data[0])
                        else f"Column {col_idx + 1}",
                        "suggestion": "Categorical column with case variations - standardize case for consistency",
                        "unique_values": len(set(sample_values)),
                        "examples": list(set(sample_values))[:5],
                    }
                )

        return hints

    def _is_likely_categorical_column(self, values: List[str]) -> bool:
        """Determine if a column likely contains categorical data."""
        if not values:
            return False

        # Check for limited unique values (typical for categories)
        unique_values = set(values)
        if len(unique_values) > len(values) * 0.9:  # Allow more unique values
            return False

        # Check for reasonable category lengths
        avg_length = sum(len(v) for v in values) / len(values)
        if avg_length > 50:  # Too long for categories
            return False

        # Check for mixed case (suggests categories that might need standardization)
        has_mixed_case = any(v != v.lower() and v != v.upper() for v in values)

        return has_mixed_case and len(unique_values) <= 20

    def _apply_case_sensitivity_hints(
        self,
        spreadsheet: SpreadsheetInterface,
        hints_by_sheet: Dict[str, List[Dict[str, Any]]],
        result: ValidationResult,
    ) -> None:
        """Apply case sensitivity hints to the spreadsheet."""
        for sheet_name, hints in hints_by_sheet.items():
            # Get current sheet data
            sheet_data = spreadsheet.get_sheet_data(sheet_name)
            if not sheet_data or not sheet_data.values:
                continue

            # Create a new column for case sensitivity hints
            hint_column_idx = len(sheet_data.values[0])  # Add at the end

            # Add header for hints column
            if len(sheet_data.values[0]) <= hint_column_idx:
                # Extend the header row
                sheet_data.values[0].append("Case Sensitivity Hints")
            else:
                sheet_data.values[0][hint_column_idx] = "Case Sensitivity Hints"

            # Add hints for each row that has flags
            for hint in hints:
                if hint["type"] in [
                    "case_variations",
                    "case_sensitive_identifiers",
                    "case_sensitive_categories",
                ]:
                    # Find rows to add hints to
                    if "examples" in hint:
                        for cell_ref in hint["examples"]:
                            # Parse cell reference to get row/col
                            row_idx, col_idx = self._parse_cell_reference(cell_ref)
                            if row_idx is not None and col_idx is not None:
                                # Ensure the row has enough columns
                                while (
                                    len(sheet_data.values[row_idx]) <= hint_column_idx
                                ):
                                    sheet_data.values[row_idx].append("")

                                # Add the hint
                                current_hint = sheet_data.values[row_idx][
                                    hint_column_idx
                                ]
                                new_hint = hint["suggestion"]

                                if current_hint:
                                    new_hint = f"{current_hint}; {new_hint}"

                                sheet_data.values[row_idx][hint_column_idx] = new_hint

                                # Report the detailed fix
                                result.add_detailed_fix(
                                    sheet_name=sheet_name,
                                    cell=cell_ref,
                                    message=f"Added case sensitivity hint: {new_hint}",
                                    old_value="",
                                    new_value=new_hint,
                                )

            # Update the sheet
            spreadsheet.update_sheet_data(
                sheet_name=sheet_name,
                values=sheet_data.values,
                start_row=1,
                start_col=1,
            )

    def _parse_cell_reference(self, cell_ref: str) -> tuple[int | None, int | None]:
        """Parse a cell reference to get row and column indices."""
        try:
            # Handle sheet references like 'Sheet1!A1'
            if "!" in cell_ref:
                cell_ref = cell_ref.split("!")[1]

            # Extract column letters and row number
            col_match = re.match(r"^([A-Z]+)", cell_ref)
            row_match = re.search(r"(\d+)$", cell_ref)

            if not col_match or not row_match:
                return None, None

            # Convert column letters to index
            col_letters = col_match.group(1)
            col_idx = 0
            for letter in col_letters:
                col_idx = col_idx * 26 + (ord(letter) - ord("A") + 1)
            col_idx -= 1  # Convert to 0-based

            # Convert row number to index
            row_idx = int(row_match.group(1)) - 1  # Convert to 0-based

            return row_idx, col_idx
        except (ValueError, IndexError):
            return None, None
