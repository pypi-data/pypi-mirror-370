"""Cell Value Validation Validator.

This validator checks if expected values match actual values in specified cells,
supporting configuration-based expected value lists and handling data type
mismatches.
"""

from typing import Any, Dict, List, Union, Optional
from pathlib import Path

from urarovite.validators.base import BaseValidator


class CellValueValidationValidator(BaseValidator):
    """Validator for checking cell values against expected values."""

    def __init__(self) -> None:
        """Initialize the cell value validation validator."""
        super().__init__(
            validator_id="cell_value_validation",
            name="Cell Value Validation",
            description="Check if expected values match actual values in "
            "specified cells",
        )

    def validate(
        self,
        spreadsheet_source: Union[str, Path, Any],
        mode: str,
        auth_credentials: Dict[str, Any] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Execute the cell value validation check.

        Args:
            spreadsheet_source: Either a Google Sheets URL, Excel file path,
                or SpreadsheetInterface
            mode: Either "fix" (auto-correct) or "flag" (report only)
            auth_credentials: Authentication credentials (required for
                Google Sheets)
            **kwargs: Additional parameters including:
                - expected_values: Dict mapping cell references to expected
                    values
                - sheet_name: Optional sheet name to validate
                - tolerance: Numeric tolerance for floating point
                    comparisons

        Returns:
            Dict with validation results

        Raises:
            ValidationError: If validation fails
        """

        def validation_logic(spreadsheet, result, **kwargs):
            """Format-agnostic validation logic."""
            # Get expected values from kwargs
            expected_values = kwargs.get("expected_values", {})
            sheet_name = kwargs.get("sheet_name")
            tolerance = kwargs.get("tolerance", 0.001)

            if not expected_values:
                result.add_error(
                    f"{self.id} validator: No expected values provided for validation"
                )
                return

            # Validate input parameters
            if not isinstance(expected_values, dict):
                result.add_error(
                    f"{self.id} validator: expected_values must be a dictionary"
                )
                return

            if not isinstance(tolerance, (int, float)):
                result.add_error(f"{self.id} validator: tolerance must be a number")
                return

            if tolerance < 0:
                result.add_error(f"{self.id} validator: tolerance must be non-negative")
                return

            # Validate expected_values keys are valid cell references
            invalid_refs = []
            for cell_ref in expected_values.keys():
                if not isinstance(cell_ref, str) or not cell_ref.strip():
                    invalid_refs.append(cell_ref)
                    continue
                # Quick format check - should start with letter and have
                # numbers
                if not any(c.isalpha() for c in cell_ref) or not any(
                    c.isdigit() for c in cell_ref
                ):
                    invalid_refs.append(cell_ref)

            if invalid_refs:
                result.add_error(
                    f"{self.id} validator: Invalid cell reference format(s): {invalid_refs[:5]}"
                    + ("..." if len(invalid_refs) > 5 else "")
                )
                return

            # Validate sheet_name if provided
            if sheet_name is not None and not isinstance(sheet_name, str):
                result.add_error(f"{self.id} validator: sheet_name must be a string")
                return

            # Get sheet data using base class helper
            sheet_data, actual_sheet_name = self._get_all_sheet_data(
                spreadsheet, sheet_name
            )

            # Validate cell values
            discrepancies = self._validate_cell_values(
                sheet_data, expected_values, tolerance, actual_sheet_name
            )

            if mode == "fix":
                # Apply fixes by updating cells with expected values
                fixes_applied = self._apply_fixes(
                    spreadsheet, actual_sheet_name, discrepancies, result
                )
                result.set_automated_log(
                    f"Applied {fixes_applied} fixes to cell values"
                )
            else:
                # Flag flags without fixing - add detailed issue reporting
                for discrepancy in discrepancies:
                    if discrepancy.get("issue") == "Value mismatch":
                        result.add_detailed_issue(
                            sheet_name=actual_sheet_name,
                            cell=discrepancy.get("cell_reference", "unknown"),
                            message=f"Expected '{discrepancy.get('expected_value')}' "
                            f"but found '{discrepancy.get('actual_value')}'",
                            value=discrepancy.get("actual_value"),
                        )
                    else:
                        # Handle other types of flags (invalid refs, etc.)
                        result.add_detailed_issue(
                            sheet_name=actual_sheet_name,
                            cell=discrepancy.get("cell_reference", "unknown"),
                            message=discrepancy.get("issue", "Unknown issue"),
                            value=discrepancy.get("actual_value"),
                        )

                result.set_automated_log(
                    f"Found {len(discrepancies)} cell value discrepancies"
                )

            # Add discrepancy details to result
            result.details["discrepancies"] = discrepancies
            result.details["total_cells_checked"] = len(expected_values)

        return self._execute_validation(
            validation_logic, spreadsheet_source, auth_credentials, **kwargs
        )

    def _validate_cell_values(
        self,
        sheet_data: List[List[Any]],
        expected_values: Dict[str, Any],
        tolerance: float,
        sheet_name: str,
    ) -> List[Dict[str, Any]]:
        """Validate cell values against expected values.

        Args:
            sheet_data: 2D list of cell values from the sheet
            expected_values: Dict mapping cell references to expected values
            tolerance: Numeric tolerance for floating point comparisons
            sheet_name: Name of the sheet being validated

        Returns:
            List of discrepancy dictionaries with cell reference and details
        """
        discrepancies = []

        for cell_ref, expected_value in expected_values.items():
            try:
                # Parse cell reference (e.g., "A1", "B2")
                row_idx, col_idx = self._parse_cell_reference(cell_ref)

                # Generate full cell reference with sheet name for reporting
                full_cell_ref = self._generate_cell_reference(
                    row_idx, col_idx, sheet_name
                )

                # Get actual value from sheet data
                if 0 <= row_idx < len(sheet_data) and 0 <= col_idx < len(
                    sheet_data[row_idx]
                ):
                    actual_value = sheet_data[row_idx][col_idx]
                else:
                    # Cell reference is out of bounds
                    discrepancies.append(
                        {
                            "cell_reference": full_cell_ref,
                            "expected_value": expected_value,
                            "actual_value": None,
                            "issue": "Cell reference out of bounds",
                            "row": row_idx + 1,
                            "column": col_idx + 1,
                        }
                    )
                    continue

                # Check if values match
                if not self._values_match(actual_value, expected_value, tolerance):
                    discrepancies.append(
                        {
                            "cell_reference": full_cell_ref,
                            "expected_value": expected_value,
                            "actual_value": actual_value,
                            "issue": "Value mismatch",
                            "row": row_idx + 1,
                            "column": col_idx + 1,
                            "data_type_mismatch": self._detect_data_type_mismatch(
                                actual_value, expected_value
                            ),
                        }
                    )

            except ValueError as e:
                # Invalid cell reference format - use original cell_ref for
                # invalid ones
                discrepancies.append(
                    {
                        "cell_reference": cell_ref,
                        "expected_value": expected_value,
                        "actual_value": None,
                        "issue": f"Invalid cell reference: {str(e)}",
                        "row": None,
                        "column": None,
                    }
                )

        return discrepancies

    def _parse_cell_reference(self, cell_ref: str) -> tuple[int, int]:
        """Parse A1 notation cell reference to row and column indices.

        Args:
            cell_ref: Cell reference in A1 notation (e.g., "A1", "B2")

        Returns:
            Tuple of (row_index, column_index) where both are 0-based

        Raises:
            ValueError: If cell reference format is invalid
        """
        if not cell_ref or not isinstance(cell_ref, str):
            raise ValueError("Cell reference must be a non-empty string")

        # Find the boundary between letters and numbers
        boundary = 0
        for i, char in enumerate(cell_ref):
            if char.isdigit():
                boundary = i
                break

        if boundary == 0:
            raise ValueError(f"Invalid cell reference format: {cell_ref}")

        # Parse column (letters to column index)
        col_str = cell_ref[:boundary].upper()
        col_idx = 0
        for char in col_str:
            if not char.isalpha():
                raise ValueError(f"Invalid column reference: {col_str}")
            col_idx = col_idx * 26 + (ord(char) - ord("A") + 1)
        col_idx -= 1  # Convert to 0-based index

        # Parse row (numbers to row index)
        try:
            row_idx = int(cell_ref[boundary:]) - 1  # Convert to 0-based index
        except ValueError:
            raise ValueError(f"Invalid row reference: {cell_ref[boundary:]}")

        if row_idx < 0:
            raise ValueError(f"Row index must be positive: {cell_ref}")

        return row_idx, col_idx

    def _values_match(
        self, actual_value: Any, expected_value: Any, tolerance: float
    ) -> bool:
        """Check if actual and expected values match.

        Args:
            actual_value: The actual value from the sheet
            expected_value: The expected value to compare against
            tolerance: Numeric tolerance for floating point comparisons

        Returns:
            True if values match, False otherwise
        """
        # Handle None/empty values
        if actual_value is None or actual_value == "":
            return expected_value is None or expected_value == ""

        if expected_value is None or expected_value == "":
            return actual_value is None or actual_value == ""

        # Convert both values to strings for comparison
        actual_str = str(actual_value).strip()
        expected_str = str(expected_value).strip()

        # Exact string match
        if actual_str == expected_str:
            return True

        # Try numeric comparison with tolerance
        try:
            actual_num = float(actual_str)
            expected_num = float(expected_str)
            return abs(actual_num - expected_num) <= tolerance
        except (ValueError, TypeError):
            # Not numeric, so no match
            pass

        # Try case-insensitive string comparison
        if actual_str.lower() == expected_str.lower():
            return True

        return False

    def _detect_data_type_mismatch(
        self, actual_value: Any, expected_value: Any
    ) -> Optional[str]:
        """Detect data type mismatches between actual and expected values.

        Args:
            actual_value: The actual value from the sheet
            expected_value: The expected value to compare against

        Returns:
            Description of the data type mismatch, or None if no mismatch
        """
        if actual_value is None or expected_value is None:
            return None

        actual_type = type(actual_value)
        expected_type = type(expected_value)

        # Check for string vs number mismatch
        if isinstance(actual_value, (int, float)) and isinstance(expected_value, str):
            try:
                # Try to convert expected string to number
                float(expected_value)
                return "Expected string but found number"
            except ValueError:
                return "Expected string but found number (non-convertible)"

        elif isinstance(actual_value, str) and isinstance(expected_value, (int, float)):
            try:
                # Try to convert actual string to number
                float(actual_value)
                return "Expected number but found string (convertible)"
            except ValueError:
                return "Expected number but found string (non-convertible)"

        # Check for other type mismatches
        elif actual_type != expected_type:
            return (
                f"Type mismatch: expected {expected_type.__name__}, "
                f"got {actual_type.__name__}"
            )

        return None

    def _apply_fixes(
        self,
        spreadsheet: Any,
        sheet_name: str,
        discrepancies: List[Dict[str, Any]],
        result: Any,
    ) -> int:
        """Apply fixes by updating cells with expected values.

        Args:
            spreadsheet: Spreadsheet interface
            sheet_name: Name of the sheet to update
            discrepancies: List of discrepancies to fix
            result: ValidationResult instance for detailed reporting

        Returns:
            Number of fixes applied
        """
        fixes_applied = 0

        # Only fix discrepancies that are actual value mismatches, not invalid
        # references
        fixable_discrepancies = [
            disc
            for disc in discrepancies
            if disc.get("issue") == "Value mismatch"
            and disc.get("row") is not None
            and disc.get("column") is not None
        ]

        for discrepancy in fixable_discrepancies:
            try:
                expected_value = discrepancy["expected_value"]
                row = discrepancy["row"]  # Already 1-based
                column = discrepancy["column"]  # Already 1-based
                cell_ref = discrepancy["cell_reference"]

                # Store old value for detailed reporting
                old_value = discrepancy.get("actual_value")

                # Update the cell with expected value using
                # SpreadsheetInterface
                spreadsheet.update_cell_value(
                    sheet_name=sheet_name, row=row, column=column, value=expected_value
                )

                # Add detailed fix reporting
                result.add_detailed_fix(
                    sheet_name=sheet_name,
                    cell=cell_ref,
                    message=f"Updated cell value from '{old_value}' "
                    f"to '{expected_value}'",
                    old_value=old_value,
                    new_value=expected_value,
                )

                self.logger.debug(f"Fixed cell {cell_ref} with value: {expected_value}")

            except Exception as e:
                self.logger.warning(
                    f"Failed to fix cell "
                    f"{discrepancy.get('cell_reference', 'unknown')}: "
                    f"{str(e)}"
                )

        return fixes_applied
