"""Numeric Rounding Rules Validator.

This validator detects inconsistent number rounding across sheets, validates decimal
place consistency, checks for precision loss in calculations, and suggests
standardized rounding rules.
"""

from typing import Any, Dict, List, Union, Optional
from pathlib import Path
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from urarovite.validators.base import BaseValidator, ValidationResult
from urarovite.core.spreadsheet import SpreadsheetInterface


class NumericRoundingValidator(BaseValidator):
    """Validator for detecting numeric rounding inconsistencies and precision flags."""

    def __init__(self) -> None:
        super().__init__(
            validator_id="numeric_rounding",
            name="Numeric Rounding Rules Validator",
            description="Detects inconsistent number rounding across sheets, validates "
            "decimal place consistency, checks for precision loss in "
            "calculations, and suggests standardized rounding rules",
        )

    def _is_numeric_value(self, value: Any) -> bool:
        """Check if a value is numeric (int, float, or numeric string).

        Args:
            value: Value to check

        Returns:
            True if numeric, False otherwise
        """
        # Explicitly exclude boolean values first (since bool is a subclass of int)
        if isinstance(value, bool):
            return False

        if isinstance(value, (int, float)):
            return True

        if isinstance(value, str):
            # Remove common formatting characters
            cleaned = value.strip().replace(",", "").replace("$", "").replace("%", "")
            # Check if it's a valid number
            try:
                float(cleaned)
                return True
            except ValueError:
                return False

        return False

    def _extract_numeric_info(self, value: Any) -> Optional[Dict[str, Any]]:
        """Extract numeric information from a value.

        Args:
            value: Value to analyze

        Returns:
            Dict with numeric info or None if not numeric
        """
        if not self._is_numeric_value(value):
            return None

        try:
            # Convert to Decimal for precise analysis
            if isinstance(value, str):
                # Clean the string
                cleaned = (
                    value.strip().replace(",", "").replace("$", "").replace("%", "")
                )
                decimal_val = Decimal(cleaned)
            else:
                decimal_val = Decimal(str(value))

            # Get decimal places
            decimal_str = str(decimal_val)
            if "." in decimal_str:
                decimal_places = len(decimal_str.split(".")[-1])
            else:
                decimal_places = 0

            # Check if it appears to be rounded
            appears_rounded = self._appears_rounded(decimal_val, decimal_places)

            return {
                "value": decimal_val,
                "decimal_places": decimal_places,
                "appears_rounded": appears_rounded,
                "original_value": value,
                "is_integer": decimal_val == decimal_val.to_integral_value(),
            }
        except (InvalidOperation, ValueError):
            return None

    def _appears_rounded(self, value: Decimal, decimal_places: int) -> bool:
        """Check if a value appears to be rounded to the given decimal places.

        Args:
            value: Decimal value to check
            decimal_places: Number of decimal places

        Returns:
            True if the value appears rounded
        """
        if decimal_places == 0:
            # For 0 decimal places, check if the value is actually an integer
            # This means no decimal part or only zeros after decimal point
            return value == value.to_integral_value()

        # Round to the specified decimal places and check if it matches
        rounded = value.quantize(
            Decimal("0." + "0" * decimal_places), rounding=ROUND_HALF_UP
        )
        return value == rounded

    def _detect_precision_loss(
        self, values_with_location: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Detect potential precision loss in calculations.

        Args:
            values_with_location: List of dicts with numeric values and their locations

        Returns:
            List of precision loss flags with sheet/cell info
        """
        flags = []

        if len(values_with_location) < 2:
            return flags

        # Check for floating point precision flags
        for val_info in values_with_location:
            val = val_info["value"]
            sheet = val_info["sheet"]
            cell = val_info["cell"]

            if val == 0:
                continue

            # Check if value is very close to a "nice" number but NOT exactly equal
            nice_numbers = [
                Decimal("0.1"),
                Decimal("0.25"),
                Decimal("0.5"),
                Decimal("0.75"),
                Decimal("1"),
                Decimal("2"),
                Decimal("5"),
                Decimal("10"),
            ]

            for nice_num in nice_numbers:
                # Only flag if close but NOT exactly equal (avoid "1 instead of 1" messages)
                difference = abs(val - nice_num)
                tolerance = nice_num * Decimal("0.00001")

                if difference > 0 and difference <= tolerance:
                    flags.append(
                        {
                            "value": val,
                            "nice_number": nice_num,
                            "difference": difference,
                            "sheet": sheet,
                            "cell": cell,
                            "suggestion": f"Consider using {nice_num} instead of {val}",
                        }
                    )
                    break

        return flags

    def _suggest_rounding_rules(
        self, decimal_places_distribution: Dict[int, int]
    ) -> List[str]:
        """Suggest standardized rounding rules based on data analysis.

        Args:
            decimal_places_distribution: Distribution of decimal places found

        Returns:
            List of rounding rule suggestions
        """
        suggestions = []

        if not decimal_places_distribution:
            return suggestions

        # Find most common decimal places
        most_common = max(decimal_places_distribution.items(), key=lambda x: x[1])

        if most_common[1] > 1:  # If we have multiple values with same decimal places
            suggestions.append(
                f"Standardize to {most_common[0]} decimal places "
                f"(found {most_common[1]} values with this precision)"
            )

        # Suggest based on common patterns
        if 0 in decimal_places_distribution and decimal_places_distribution[0] > 1:
            suggestions.append(
                "Consider using whole numbers for values that don't require decimal precision"
            )

        if 2 in decimal_places_distribution and decimal_places_distribution[2] > 1:
            suggestions.append(
                "Consider standardizing currency/percentage values to 2 decimal places"
            )

        if 4 in decimal_places_distribution and decimal_places_distribution[4] > 1:
            suggestions.append(
                "Consider if 4 decimal places are necessary - this may indicate over-precision"
            )

        return suggestions

    def validate(
        self,
        spreadsheet_source: Union[str, Path, SpreadsheetInterface],
        mode: str,
        auth_credentials: Dict[str, Any] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Validate numeric rounding consistency across sheets.

        Args:
            spreadsheet_source: Either a Google Sheets URL, Excel file path,
                or SpreadsheetInterface
            mode: Either "fix" (standardize rounding) or "flag" (report only)
            auth_credentials: Authentication credentials (required for
                Google Sheets)

        Returns:
            Dict with validation results
        """

        def validation_logic(
            spreadsheet: SpreadsheetInterface, result: ValidationResult, **kwargs
        ) -> None:
            all_numeric_values_with_location: List[Dict[str, Any]] = []
            decimal_places_distribution: Dict[int, int] = {}
            rounding_inconsistencies: List[Dict[str, Any]] = []
            precision_loss_flags: List[Dict[str, Any]] = []
            fixes_by_sheet: Dict[str, List[Dict[str, Any]]] = {}

            def process_sheet(
                tab_name: str, data: List[List[Any]], result: ValidationResult
            ) -> None:
                sheet_fixes = []

                # Process each cell in this tab
                for row_idx, row in enumerate(data):
                    for col_idx, cell in enumerate(row):
                        numeric_info = self._extract_numeric_info(cell)
                        if numeric_info:
                            value = numeric_info["value"]
                            decimal_places = numeric_info["decimal_places"]
                            cell_ref = self._generate_cell_reference(
                                row_idx, col_idx, tab_name
                            )

                            # Track decimal places distribution
                            decimal_places_distribution[decimal_places] = (
                                decimal_places_distribution.get(decimal_places, 0) + 1
                            )

                            # Collect numeric values with location info for precision analysis
                            all_numeric_values_with_location.append(
                                {
                                    "value": value,
                                    "sheet": tab_name,
                                    "cell": cell_ref,
                                    "decimal_places": decimal_places,
                                }
                            )

                            # Check for rounding inconsistencies
                            if (
                                not numeric_info["appears_rounded"]
                                and decimal_places > 0
                            ):
                                rounding_inconsistencies.append(
                                    {
                                        "sheet": tab_name,
                                        "cell": cell_ref,
                                        "value": str(value),
                                        "decimal_places": decimal_places,
                                        "suggestion": f"Consider rounding to {decimal_places} decimal places",
                                    }
                                )

                                # Prepare fix if in fix mode
                                if mode == "fix":
                                    # Round to the detected decimal places
                                    rounded_value = value.quantize(
                                        Decimal("0." + "0" * decimal_places),
                                        rounding=ROUND_HALF_UP,
                                    )
                                    sheet_fixes.append(
                                        {
                                            "row": row_idx,
                                            "col": col_idx,
                                            "new_value": float(rounded_value),
                                        }
                                    )

                # Store fixes for this sheet
                if sheet_fixes:
                    fixes_by_sheet[tab_name] = sheet_fixes

            # Process all sheets using the base class helper
            self._process_all_sheets(spreadsheet, process_sheet, result)

            # Detect precision loss across all values
            precision_loss_flags = self._detect_precision_loss(
                all_numeric_values_with_location
            )

            # Generate rounding rule suggestions
            rounding_suggestions = self._suggest_rounding_rules(
                decimal_places_distribution
            )

            # Apply fixes if in fix mode
            if mode == "fix" and fixes_by_sheet:
                for sheet_name, fixes in fixes_by_sheet.items():
                    sheet_data = spreadsheet.get_sheet_data(sheet_name)
                    if sheet_data and sheet_data.values:
                        self._apply_fixes_to_sheet(
                            spreadsheet, sheet_name, sheet_data.values, fixes
                        )

                        # Add detailed fix reporting for each applied fix
                        for fix in fixes:
                            cell_ref = self._generate_cell_reference(
                                fix["row"], fix["col"], sheet_name
                            )
                            original_value = sheet_data.values[fix["row"]][fix["col"]]
                            result.add_detailed_fix(
                                sheet_name=sheet_name,
                                cell=cell_ref,
                                message=f"Rounded value from {original_value} to {fix['new_value']}",
                                old_value=str(original_value),
                                new_value=str(fix["new_value"]),
                            )

                # Save changes
                spreadsheet.save()

                total_fixes_applied = sum(
                    len(fixes) for fixes in fixes_by_sheet.values()
                )
                result.set_automated_log(
                    f"Applied {total_fixes_applied} rounding fixes across "
                    f"{len(fixes_by_sheet)} sheets"
                )
            else:
                # Flag mode - add detailed issue reporting
                for inconsistency in rounding_inconsistencies:
                    result.add_detailed_issue(
                        sheet_name=inconsistency["sheet"],
                        cell=inconsistency["cell"],
                        message=f"Value {inconsistency['value']} has {inconsistency['decimal_places']} "
                        f"decimal places but appears unrounded. {inconsistency['suggestion']}",
                        value=inconsistency["value"],
                    )

                for precision_issue in precision_loss_flags:
                    result.add_detailed_issue(
                        sheet_name=precision_issue["sheet"],
                        cell=precision_issue["cell"],
                        message=f"Value {precision_issue['value']} is very close to "
                        f"{precision_issue['nice_number']}. {precision_issue['suggestion']}",
                        value=str(precision_issue["value"]),
                    )

                total_flags = len(rounding_inconsistencies) + len(precision_loss_flags)
                if total_flags > 0:
                    result.set_automated_log(
                        f"Found {total_flags} numeric rounding flags: "
                        f"{len(rounding_inconsistencies)} inconsistent values and "
                        f"{len(precision_loss_flags)} precision concerns"
                    )
                else:
                    result.set_automated_log("No numeric rounding flags found")

            # Set result details
            result.details["decimal_places_distribution"] = decimal_places_distribution
            result.details["rounding_inconsistencies"] = rounding_inconsistencies
            result.details["precision_loss_flags"] = precision_loss_flags
            result.details["rounding_suggestions"] = rounding_suggestions
            result.details["total_numeric_values"] = len(
                all_numeric_values_with_location
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
    """Backward compatibility function for the numeric rounding validator.

    Args:
        spreadsheet_source: Either a Google Sheets URL, Excel file path,
            or SpreadsheetInterface
        mode: Either "fix" (standardize rounding) or "flag" (report only)
        auth_credentials: Authentication credentials (required for
            Google Sheets)

    Returns:
        Dict with validation results
    """
    validator = NumericRoundingValidator()
    return validator.validate(spreadsheet_source, mode, auth_credentials, **kwargs)
