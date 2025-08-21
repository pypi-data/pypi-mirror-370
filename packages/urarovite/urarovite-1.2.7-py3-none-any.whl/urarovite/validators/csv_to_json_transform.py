"""
CSV to JSON Transform Validator.

This validator transforms per-row CSV task data into a structured JSON format
with the standardized fields: Prompt, Input File, Output File, Input Excel File,
Output Excel File, Verification Field Ranges, Field Mask, Case Sensitivity,
Numeric Rounding, Color matching, Editor Fixes, Editor Comments, Estimated Task Length.

Goal:
Transform CSV task data into a standardized JSON schema format for data processing.

Why:
Provides a consistent data structure for downstream processing while maintaining
the original CSV data and adding template fields for future use.
"""

from __future__ import annotations
import json
import re
from typing import Any, Dict, List, Union
from pathlib import Path

from urarovite.validators.base import BaseValidator, ValidationResult
from urarovite.core.exceptions import ValidationError
from urarovite.core.spreadsheet import SpreadsheetInterface
from urarovite.utils.sheets import (
    fetch_sheet_tabs,
    get_sheet_values,
    update_sheet_values,
)


class CSVToJSONTransformValidator(BaseValidator):
    """Validator that transforms CSV task data to JSON format."""

    def __init__(self) -> None:
        super().__init__(
            validator_id="csv_to_json_transform",
            name="CSV to JSON Transform",
            description=(
                "Transform the task CSV into JSON with fields: Prompt, Input File, "
                "Output File, Input Excel File, Output Excel File, Verification Field Ranges, "
                "Field Mask, Case Sensitivity, Numeric Rounding, Color matching, "
                "Editor Fixes, Editor Comments, Estimated Task Length. "
                "Detects and fixes malformed A1 range notation (missing quotes/exclamation marks)."
            ),
        )

    # worker_id,task_id,task_response_id,job domain,description,prompt,verification_criteria,verification_field_ranges,input_sheet_url,example_output_sheet_url
    # Field mapping from CSV columns to standardized JSON field names (snake_case)
    FIELD_MAPPING = {
        "worker_id": "worker_id",
        "task_id": "task_id",
        "task_response_id": "task_response_id",
        "job domain": "job_domain",
        "description": "description",
        "prompt": "prompt",
        "verification_criteria": "verification_criteria",
        "verification_field_ranges": "verification_field_ranges",
        "input_sheet_url": "input_file",
        "example_output_sheet_url": "output_file",
    }

    # Template for fields not present in source CSV - set to "NA"
    TEMPLATE_FIELDS = {
        "input_excel_file": "NA",
        "output_excel_file": "NA",
        "field_mask": "NA",
        "case_sensitivity": "NA",
        "numeric_rounding": "NA",
        "color_matching": "NA",
        "editor_fixes": "NA",
        "editor_comments": "NA",
        "estimated_task_length": "NA",
    }

    def _detect_malformed_a1_range(self, value: str) -> bool:
        if not value or not isinstance(value, str):
            return False

        # Pattern for valid A1 range: [A-Z]+\d+:[A-Z]+\d+
        a1_pattern = r"[A-Z]+\d+:[A-Z]+\d+"

        # Check if it contains an A1 range pattern
        if not re.search(a1_pattern, value):
            return False

        # Valid format should be: 'SheetName'!A1:B10 or just A1:B10
        # If it contains a sheet reference, it should be properly quoted

        # Case 1: Has sheet reference but missing opening quote: "SheetName'!A1:B10"
        if re.search(r"^[^']+\s*'!" + a1_pattern + r"$", value):
            return True

        # Case 2: Has sheet reference but missing exclamation: "SheetName'A1:B10" or "'SheetName'A1:B10"
        if re.search(r"^.+'[A-Z]+\d+:[A-Z]+\d+$", value) and "!" not in value:
            return True

        # Case 3: Has sheet reference but missing both quotes and exclamation: "SheetNameA1:B10"
        if "!" not in value and "'" not in value:
            # If it's just a pure range like "A1:B10", it's valid
            if re.match(r"^" + a1_pattern + r"$", value):
                return False
            # If there are characters before the range, it's likely a malformed sheet reference
            if re.search(r"^.+" + a1_pattern + r"$", value):
                return True

        return False

    def _fix_a1_range(self, value: str) -> str:
        if not self._detect_malformed_a1_range(value):
            return value

        a1_pattern = r"[A-Z]+\d+:[A-Z]+\d+"

        # Case 1: Missing opening quote: "SheetName'!A1:B10" → "'SheetName'!A1:B10"
        match = re.match(r"^([^']+)\s*'!(" + a1_pattern + r")$", value)
        if match:
            sheet_name, range_part = match.groups()
            return f"'{sheet_name.strip()}'!{range_part}"

        # Case 2: Missing exclamation: "SheetName'A1:B10" or "'SheetName'A1:B10" → "'SheetName'!A1:B10"
        match = re.match(r"^(.+)'(" + a1_pattern + r")$", value)
        if match and "!" not in value:
            sheet_part, range_part = match.groups()
            # Remove quotes if already present, then add them back properly
            sheet_name = sheet_part.strip("'").strip()
            return f"'{sheet_name}'!{range_part}"

        # Case 3: Missing both quotes and exclamation: "SheetNameA1:B10" → "'SheetName'!A1:B10"
        if "!" not in value and "'" not in value:
            match = re.match(r"^(.+?)(" + a1_pattern + r")$", value)
            if match:
                sheet_name, range_part = match.groups()
                return f"'{sheet_name.strip()}'!{range_part}"

        return value

    def _transform_row(self, row_data: Dict[str, Any]) -> Dict[str, Any]:
        transformed = {}
        a1_range_fixes = []

        # Include all original CSV columns as strings (convert to snake_case)
        for csv_field, value in row_data.items():
            # Convert non-string headers to strings first
            str_field = str(csv_field) if csv_field is not None else "none"
            snake_case_field = str_field.lower().replace(" ", "_").replace("-", "_")

            if value is None or (isinstance(value, str) and not value.strip()):
                transformed[snake_case_field] = ""
            else:
                str_value = str(value)

                if self._detect_malformed_a1_range(str_value):
                    fixed_a1_value = self._fix_a1_range(str_value)
                    a1_range_fixes.append(
                        {
                            "field": snake_case_field,
                            "original": str_value,
                            "fixed": fixed_a1_value,
                        }
                    )
                    transformed[snake_case_field] = fixed_a1_value
                else:
                    transformed[snake_case_field] = str_value

        # Map specific fields to standardized names (only if different from snake_case conversion)
        for csv_field, json_field in self.FIELD_MAPPING.items():
            # Convert field to string first (like we do above)
            str_field = str(csv_field) if csv_field is not None else "none"
            snake_case_field = str_field.lower().replace(" ", "_").replace("-", "_")
            # Only apply mapping if it would result in a different field name
            if snake_case_field != json_field:
                if csv_field in row_data:
                    value = row_data[csv_field]
                    if value is None or (isinstance(value, str) and not value.strip()):
                        transformed[json_field] = ""
                    else:
                        str_value = str(value)

                        if self._detect_malformed_a1_range(str_value):
                            fixed_a1_value = self._fix_a1_range(str_value)
                            snake_case_original = (
                                csv_field.lower().replace(" ", "_").replace("-", "_")
                            )
                            if not any(
                                fix["field"] == snake_case_original
                                for fix in a1_range_fixes
                            ):
                                a1_range_fixes.append(
                                    {
                                        "field": json_field,
                                        "original": str_value,
                                        "fixed": fixed_a1_value,
                                    }
                                )
                            transformed[json_field] = fixed_a1_value
                        else:
                            transformed[json_field] = str_value
                else:
                    transformed[json_field] = ""

        transformed.update(self.TEMPLATE_FIELDS.copy())

        if a1_range_fixes:
            transformed["_a1_range_fixes"] = a1_range_fixes

        return transformed

    def _read_csv_data(
        self, sheets_service: Any, sheet_id: str
    ) -> List[Dict[str, Any]]:
        tabs_result = fetch_sheet_tabs(sheets_service, sheet_id)
        if not tabs_result["accessible"] or not tabs_result["tabs"]:
            raise ValidationError("Unable to access sheet tabs")

        sheet_name = tabs_result["tabs"][0]
        range_name = f"'{sheet_name}'"
        result = get_sheet_values(sheets_service, sheet_id, range_name)

        if not result["success"]:
            raise ValidationError(f"Failed to read sheet data: {result['error']}")

        values = result["values"]
        if not values:
            return []

        headers = values[0]
        csv_data = []

        for row_values in values[1:]:
            # Handle row length mismatches
            if len(row_values) > len(headers):
                # Truncate extra columns
                row_values = row_values[: len(headers)]
            elif len(row_values) < len(headers):
                # Pad with empty strings
                row_values = row_values + [""] * (len(headers) - len(row_values))

            row_dict = dict(zip(headers, row_values))
            csv_data.append(row_dict)

        return csv_data

    def _write_json_output(
        self, sheets_service: Any, sheet_id: str, json_data: List[Dict[str, Any]]
    ) -> None:
        if not json_data:
            return

        # Get the original sheet name
        tabs_result = fetch_sheet_tabs(sheets_service, sheet_id)
        if not tabs_result["accessible"] or not tabs_result["tabs"]:
            raise ValidationError("Unable to access sheet tabs")

        sheet_name = tabs_result["tabs"][0]

        # Get current sheet data to find the next available column
        result = get_sheet_values(sheets_service, sheet_id, f"'{sheet_name}'")
        if not result["success"]:
            raise ValidationError(f"Failed to read sheet data: {result['error']}")

        current_values = result["values"]
        if not current_values:
            raise ValidationError("No data found in sheet")

        # Calculate next column (after existing data)
        max_columns = max(len(row) for row in current_values) if current_values else 0
        next_col_letter = self._get_column_letter(max_columns + 1)

        # Create JSON output column data
        json_output_values = [["JSON_Output"]]  # Header
        for record in json_data:
            # Convert entire record to a single JSON string
            json_string = json.dumps(record, ensure_ascii=False)
            json_output_values.append([json_string])

        # Write JSON column to the sheet
        range_name = f"'{sheet_name}'!{next_col_letter}1"
        update_result = update_sheet_values(
            sheets_service, sheet_id, range_name, json_output_values
        )

        if not update_result["success"]:
            raise ValidationError(
                f"Failed to write JSON output: {update_result['error']}"
            )

    def _get_column_letter(self, col_num: int) -> str:
        """Convert column number to Excel column letter (1=A, 2=B, 27=AA, etc.)"""
        result = ""
        while col_num > 0:
            col_num -= 1
            result = chr(65 + (col_num % 26)) + result
            col_num //= 26
        return result

    def validate(
        self,
        spreadsheet_source: Union[str, Path, SpreadsheetInterface],
        mode: str,
        auth_credentials: Dict[str, Any] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Transform CSV data to JSON format with A1 range fixes.

        Args:
            spreadsheet_source: Either a Google Sheets URL, Excel file path,
                or SpreadsheetInterface
            mode: Either "fix" (transform and write) or "flag" (report only)
            auth_credentials: Authentication credentials (required for Google Sheets)

        Returns:
            Dict with validation results
        """

        def validation_logic(
            spreadsheet: SpreadsheetInterface, result: ValidationResult, **kwargs
        ) -> None:
            # Use generic utility that works with both Google Sheets and Excel
            try:
                from urarovite.utils.generic_spreadsheet import (
                    read_csv_data_from_spreadsheet,
                )

                csv_data = read_csv_data_from_spreadsheet(
                    spreadsheet_source, auth_credentials=auth_credentials
                )
            except Exception as e:
                result.add_error(f"Failed to read CSV data: {str(e)}")
                return

            if not csv_data:
                result.set_automated_log("No CSV data found to transform")
                return

            json_data = []

            # Get header row to determine column letters
            headers = csv_data[0].keys() if csv_data else []
            header_map = {
                header: self._get_column_letter(i + 1)
                for i, header in enumerate(headers)
            }

            for i, row in enumerate(csv_data, 1):
                transformed_row = self._transform_row(row)
                transformed_row["_row_number"] = i

                if "_a1_range_fixes" in transformed_row:
                    for fix in transformed_row["_a1_range_fixes"]:
                        # Find the original CSV column name for the fix
                        original_csv_field = next(
                            (
                                csv_field
                                for csv_field, json_field in self.FIELD_MAPPING.items()
                                if json_field == fix["field"]
                            ),
                            fix["field"].replace("_", " "),
                        )

                        col_letter = header_map.get(original_csv_field, "?")
                        cell_ref = f"{col_letter}{i + 1}"

                        result.add_detailed_fix(
                            sheet_name=spreadsheet.get_metadata().sheet_names[0],
                            cell=cell_ref,
                            message="Fixed malformed A1 range notation",
                            old_value=fix["original"],
                            new_value=fix["fixed"],
                        )

                json_data.append(transformed_row)

            result.details["total_rows"] = len(csv_data)
            result.details["transformed_rows"] = len(json_data)
            result.details["json_schema"] = (
                list(json_data[0].keys())
                if json_data
                else list(self.FIELD_MAPPING.values())
                + list(self.TEMPLATE_FIELDS.keys())
            )
            result.details["sample_output"] = json_data[:3] if json_data else []

            if mode == "fix":
                if json_data:
                    # Use generic utility that works with both Google Sheets and Excel
                    from urarovite.utils.generic_spreadsheet import (
                        write_json_to_spreadsheet,
                    )

                    write_json_to_spreadsheet(
                        spreadsheet_source, json_data, auth_credentials=auth_credentials
                    )

                    log_msg = f"Transformed {len(json_data)} rows to JSON format and wrote to sheet"
                    if result.fixes_applied > 0:
                        log_msg += (
                            f". Applied {result.fixes_applied} A1 range notation fixes"
                        )
                    result.set_automated_log(log_msg)
                else:
                    result.set_automated_log("No rows to transform")
            else:  # flag mode
                result.add_issue(
                    result.fixes_applied
                )  # In flag mode, fixes are reported as flags
                log_msg = f"Would transform {len(json_data)} rows to JSON format"
                if result.flags_found > 0:
                    log_msg += (
                        f". Would apply {result.flags_found} A1 range notation fixes"
                    )
                result.set_automated_log(log_msg)

        return self._execute_validation(
            validation_logic, spreadsheet_source, auth_credentials, **kwargs
        )


def transform_csv_to_json(csv_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    validator = CSVToJSONTransformValidator()
    json_data = []

    for i, row in enumerate(csv_data, 1):
        try:
            transformed_row = validator._transform_row(row)
            transformed_row["_row_number"] = i
            json_data.append(transformed_row)
        except Exception:
            continue

    return json_data
