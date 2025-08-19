"""
Spreadsheet Differences Validator - Fixed Column C Writing.

This validator compares spreadsheets referenced in columns A and B,
then generates a detailed JSON report of all differences found.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Union

from urarovite.core.spreadsheet import SpreadsheetFactory, SpreadsheetInterface
from urarovite.utils.sheets import extract_sheet_id, fetch_workbook_with_formulas
from urarovite.validators.base import BaseValidator, ValidationResult


class SpreadsheetDifferencesValidator(BaseValidator):
    """Validator that compares two spreadsheets and reports differences."""

    def __init__(self) -> None:
        super().__init__(
            validator_id="spreadsheet_differences",
            name="Spreadsheet Differences",
            description=(
                "Compares spreadsheets in columns A and B and reports all differences"
            ),
        )

    def _get_sheet_data_with_hyperlinks(
        self, spreadsheet: SpreadsheetInterface, sheet_name: str
    ) -> list[list[Any]]:
        """
        Fetches sheet data, resolving hyperlinks to their URLs.
        If a cell has a hyperlink, its URL is used. Otherwise, the formatted value is used.
        """
        # Check if it's a Google Sheet by checking for specific attributes
        if not hasattr(spreadsheet, "sheets_service") or not hasattr(
            spreadsheet, "spreadsheet"
        ):
            sheet_data_obj = spreadsheet.get_sheet_data(sheet_name)
            return sheet_data_obj.values if sheet_data_obj else []

        try:
            g_spreadsheet: Any = spreadsheet  # To satisfy type checkers
            worksheet = g_spreadsheet.spreadsheet.worksheet(sheet_name)
            sheet_gid = worksheet.id

            workbook_data = (
                g_spreadsheet.sheets_service.spreadsheets()
                .get(
                    spreadsheetId=g_spreadsheet.spreadsheet.id,
                    fields="sheets(properties.sheetId,data.rowData.values(formattedValue,hyperlink))",
                )
                .execute()
            )

            sheet_data = None
            for s in workbook_data.get("sheets", []):
                if s.get("properties", {}).get("sheetId") == sheet_gid:
                    sheet_data = s
                    break

            if not sheet_data:
                return []

            rows = []
            grid_data = sheet_data.get("data", [{}])[0]
            for row_data in grid_data.get("rowData", []):
                row_values = []
                if "values" in row_data:
                    for cell in row_data.get("values", []):
                        if "hyperlink" in cell:
                            row_values.append(cell["hyperlink"])
                        else:
                            row_values.append(cell.get("formattedValue", ""))
                rows.append(row_values)

            if rows:
                max_len = max((len(row) for row in rows), default=0)
                for row in rows:
                    row.extend([""] * (max_len - len(row)))

            return rows

        except Exception:
            # Fallback to the standard method on any error
            sheet_data_obj = spreadsheet.get_sheet_data(sheet_name)
            return sheet_data_obj.values if sheet_data_obj else []

    def _compare_workbooks(
        self, input_wb: Dict[str, Any], output_wb: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compare two workbooks and return detailed differences."""
        differences = {
            "equal": True,
            "differences": [],
            "summary": {"total_differences": 0},
        }

        # Get the first sheet from each workbook
        input_sheets = input_wb.get("sheets", []) if isinstance(input_wb, dict) else []
        output_sheets = (
            output_wb.get("sheets", []) if isinstance(output_wb, dict) else []
        )

        if not input_sheets or not output_sheets:
            return differences

        # Compare the first sheet of each workbook
        self._compare_sheets(input_sheets[0], output_sheets[0], differences)

        return differences

    def _compare_sheets(
        self,
        input_sheet: Dict[str, Any],
        output_sheet: Dict[str, Any],
        differences: Dict[str, Any],
    ) -> None:
        """Compare two sheets and append differences."""
        sheet_name = (
            input_sheet.get("properties", {}).get("title", "Sheet1")
            if isinstance(input_sheet, dict)
            else "Sheet1"
        )

        # Extract row data
        input_data = []
        output_data = []

        if isinstance(input_sheet, dict):
            data = input_sheet.get("data", {})
            if isinstance(data, dict):
                input_data = data.get("rowData", [])
            elif isinstance(data, list) and len(data) > 0:
                first_data = data[0]
                if isinstance(first_data, dict):
                    input_data = first_data.get("rowData", [])

        if isinstance(output_sheet, dict):
            data = output_sheet.get("data", {})
            if isinstance(data, dict):
                output_data = data.get("rowData", [])
            elif isinstance(data, list) and len(data) > 0:
                first_data = data[0]
                if isinstance(first_data, dict):
                    output_data = first_data.get("rowData", [])

        # Compare cell contents
        max_rows = max(len(input_data), len(output_data))
        for row_idx in range(max_rows):
            input_row = (
                input_data[row_idx] if row_idx < len(input_data) else {"values": []}
            )
            output_row = (
                output_data[row_idx] if row_idx < len(output_data) else {"values": []}
            )

            input_values = (
                input_row.get("values", []) if isinstance(input_row, dict) else []
            )
            output_values = (
                output_row.get("values", []) if isinstance(output_row, dict) else []
            )

            max_cols = max(len(input_values), len(output_values))
            for col_idx in range(max_cols):
                input_cell = (
                    input_values[col_idx] if col_idx < len(input_values) else {}
                )
                output_cell = (
                    output_values[col_idx] if col_idx < len(output_values) else {}
                )

                input_formatted = (
                    input_cell.get("formattedValue", "")
                    if isinstance(input_cell, dict)
                    else str(input_cell)
                )
                output_formatted = (
                    output_cell.get("formattedValue", "")
                    if isinstance(output_cell, dict)
                    else str(output_cell)
                )

                if input_formatted != output_formatted:
                    col_letter = self._get_column_letter(col_idx + 1)
                    cell_location = f"{col_letter}{row_idx + 1}"

                    differences["differences"].append(
                        {
                            "sheet": sheet_name,
                            "location": cell_location,
                            "input_value": input_formatted,
                            "output_value": output_formatted,
                        }
                    )
                    differences["equal"] = False
                    differences["summary"]["total_differences"] += 1

    def _get_column_letter(self, col_num: int) -> str:
        """Convert column number to Excel column letter."""
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
        """Compare spreadsheets listed in columns A and B.

        This validator:
        1. Reads the provided spreadsheet
        2. Gets URLs from columns A (input) and B (output)
        3. Compares each pair and reports differences
        4. Writes results to column C if in fix mode
        """

        def validation_logic(
            spreadsheet: SpreadsheetInterface, result: ValidationResult, **kwargs
        ) -> None:
            # Read the main sheet data
            try:
                sheet_info = spreadsheet.get_sheet_data()
                if not sheet_info:
                    result.set_automated_log("No data found in spreadsheet")
                    return

                sheet_name = sheet_info.sheet_name
                sheet_values = self._get_sheet_data_with_hyperlinks(
                    spreadsheet, sheet_name
                )

                if not sheet_values:
                    result.set_automated_log("No data found in spreadsheet")
                    return

            except Exception as e:
                result.add_error(f"Failed to read spreadsheet data: {str(e)}")
                return

            # Check if there are any Google Sheet URLs to process
            has_google_sheets_urls = False
            for row in sheet_values:
                if (
                    row
                    and len(row) > 0
                    and isinstance(row[0], str)
                    and "docs.google.com" in row[0]
                ):
                    has_google_sheets_urls = True
                    break
                if (
                    row
                    and len(row) > 1
                    and isinstance(row[1], str)
                    and "docs.google.com" in row[1]
                ):
                    has_google_sheets_urls = True
                    break

            if not has_google_sheets_urls:
                result.set_automated_log("No Google Sheet URLs found to compare.")
                return

            # Get credentials now that we know we need them
            auth_creds = os.environ.get("SPREADSHEET_SERVICE_ACCOUNT_CRED")
            if not auth_creds:
                auth_creds = (
                    auth_credentials.get("encoded_credentials")
                    if auth_credentials
                    else None
                )
                if not auth_creds:
                    auth_creds = (
                        auth_credentials.get("auth_secret")
                        if auth_credentials
                        else None
                    )

            if not auth_creds:
                result.add_error(
                    "Authentication credentials not found for Google Sheets comparison"
                )
                return

            total_rows_processed = 0
            total_differences_found = 0
            all_comparisons = []

            # Build complete column C data (including existing rows)
            column_c_data = []

            # Process each row
            for row_idx, row in enumerate(sheet_values):
                # Check if first row is a header
                if row_idx == 0:
                    if row and len(row) >= 2:
                        # Check if this looks like a header
                        if isinstance(row[0], str) and isinstance(row[1], str):
                            if (
                                "url" in row[0].lower()
                                or "url" in row[1].lower()
                                or "input" in row[0].lower()
                                or "output" in row[1].lower()
                            ):
                                column_c_data.append(
                                    ["Comparison Results"]
                                )  # Add header for column C
                                continue

                # Get URLs from columns A and B
                if not row or len(row) < 2:
                    column_c_data.append([""])  # Empty result for empty row
                    continue

                input_url = row[0] if row[0] else ""
                output_url = row[1] if row[1] else ""

                # Validate URLs
                if not input_url or not output_url:
                    column_c_data.append(["No URLs provided"])
                    continue

                if not isinstance(input_url, str) or not isinstance(output_url, str):
                    column_c_data.append(["Invalid URL format"])
                    continue

                if "docs.google.com" not in input_url and "sheets" not in input_url:
                    column_c_data.append(["Invalid input URL"])
                    continue

                if "docs.google.com" not in output_url and "sheets" not in output_url:
                    column_c_data.append(["Invalid output URL"])
                    continue

                try:
                    # Extract sheet IDs
                    input_id = extract_sheet_id(input_url)
                    output_id = extract_sheet_id(output_url)

                    if not input_id or not output_id:
                        column_c_data.append(["Failed to extract sheet IDs"])
                        continue

                    # Create interfaces for each sheet
                    input_spreadsheet = SpreadsheetFactory.create_spreadsheet(
                        input_url, {"encoded_credentials": auth_creds}
                    )
                    output_spreadsheet = SpreadsheetFactory.create_spreadsheet(
                        output_url, {"encoded_credentials": auth_creds}
                    )

                    # Fetch workbooks with formulas
                    input_workbook = fetch_workbook_with_formulas(
                        input_spreadsheet.sheets_service, input_id
                    )
                    output_workbook = fetch_workbook_with_formulas(
                        output_spreadsheet.sheets_service, output_id
                    )

                    # Compare workbooks
                    comparison = self._compare_workbooks(
                        input_workbook, output_workbook
                    )

                    # Log detailed flags for each difference
                    for diff in comparison.get("differences", []):
                        result.add_detailed_issue(
                            sheet_name=diff["sheet"],
                            cell=diff["location"],
                            message="Cell content differs between spreadsheets",
                            value=(
                                f"Input: '{diff['input_value']}', "
                                f"Output: '{diff['output_value']}'"
                            ),
                        )

                    # Add metadata
                    comparison["row_number"] = row_idx + 1
                    comparison["input_url"] = input_url
                    comparison["output_url"] = output_url

                    all_comparisons.append(comparison)

                    # Prepare result for column C
                    if comparison["equal"]:
                        column_c_data.append(["✅ MATCH"])
                    else:
                        # Create a compact summary
                        diff_count = comparison["summary"]["total_differences"]

                        # Show first 3 differences in a compact format
                        diff_details = []
                        for diff in comparison["differences"][:3]:
                            diff_details.append(
                                f"{diff['location']}: '{diff['input_value']}' "
                                f"→ '{diff['output_value']}'"
                            )

                        summary_text = f"❌ {diff_count} differences found\n"
                        summary_text += "\n".join(diff_details)

                        if len(comparison["differences"]) > 3:
                            summary_text += (
                                f"\n... and {len(comparison['differences']) - 3} more"
                            )

                        column_c_data.append([summary_text])

                    if not comparison["equal"]:
                        total_differences_found += comparison["summary"][
                            "total_differences"
                        ]

                    total_rows_processed += 1

                except Exception as e:
                    # Add error result for this row
                    column_c_data.append([f"❌ ERROR: {str(e)[:100]}"])
                    result.add_error(f"Error processing row {row_idx + 1}: {str(e)}")
                    continue

            # Write results to column C if in fix mode
            if mode == "fix" and column_c_data:
                try:
                    # First, get the current sheet to check if we need to clear column C
                    current_data = spreadsheet.get_sheet_data(sheet_name)

                    # Clear any existing data in column C if needed
                    # This is important to avoid leftover data from previous runs
                    if current_data and current_data.values:
                        max_rows = len(current_data.values)
                        # Prepare a clear range for column C
                        clear_range = (
                            f"C1:C{max_rows + 10}"  # Add extra rows to be safe
                        )

                        try:
                            # Clear column C first
                            spreadsheet.clear_sheet_range(
                                sheet_name=sheet_name,
                                range_name=clear_range,
                            )
                        except Exception:
                            # If clear doesn't work, we'll overwrite anyway
                            pass

                    # Now write the new data to column C
                    # Using a specific range to ensure it writes
                    end_row = len(column_c_data)
                    update_range = f"C1:C{end_row}"

                    # Update column C with all results
                    spreadsheet.update_sheet_data(
                        sheet_name=sheet_name,
                        values=column_c_data,
                        range_name=update_range,
                    )

                    try:
                        spreadsheet.save()
                    except Exception:
                        # If save fails, we can ignore it as we already updated
                        pass

                except Exception as e:
                    result.add_error(f"Failed to write results to column C: {str(e)}")
                    # Try alternative approach - write one by one
                    try:
                        for idx, cell_value in enumerate(column_c_data):
                            if cell_value and cell_value[0]:
                                cell_range = f"C{idx + 1}"
                                spreadsheet.update_sheet_data(
                                    sheet_name=sheet_name,
                                    values=[cell_value],
                                    range_name=cell_range,
                                )
                    except Exception as e2:
                        result.add_error(f"Alternative write also failed: {str(e2)}")

            # Set result details
            result.details["total_rows_processed"] = total_rows_processed
            result.details["total_differences_found"] = total_differences_found
            result.details["comparisons"] = all_comparisons

            # Set log message
            if mode == "fix":
                log_msg = f"Processed {total_rows_processed} spreadsheet pairs"
                if total_differences_found > 0:
                    log_msg += f", found {total_differences_found} total differences."
                else:
                    log_msg += ", all spreadsheets match."
                result.set_automated_log(log_msg)
            else:
                log_msg = f"Checked {total_rows_processed} spreadsheet pairs"
                if total_differences_found > 0:
                    log_msg += f", found {total_differences_found} total differences"
                else:
                    log_msg += ", all spreadsheets match"
                result.set_automated_log(log_msg)

        return self._execute_validation(
            validation_logic, spreadsheet_source, auth_credentials, **kwargs
        )


def run(
    sheets_service: Any,
    input_sheet_url: str,
    output_sheet_url: str,
) -> Dict[str, Any]:
    """Legacy run function for backward compatibility."""
    v = SpreadsheetDifferencesValidator()
    return v.validate(
        spreadsheet_source=input_sheet_url,
        mode="flag",
        auth_credentials={"sheets_service": sheets_service},
    )
