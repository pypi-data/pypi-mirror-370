"""Google Sheets implementation of the spreadsheet interface.

This module provides Google Sheets-specific implementation of the
SpreadsheetInterface using the existing Google Sheets API utilities,
enhanced with exponential backoff for improved reliability.
"""

from typing import Any, Dict, List, Optional
from urarovite.core.spreadsheet import (
    SpreadsheetInterface,
    SpreadsheetMetadata,
    SheetData,
)
from urarovite.core.exceptions import ValidationError
from urarovite.auth.google_sheets import create_sheets_service_from_encoded_creds
from urarovite.utils.sheets import (
    extract_sheet_id,
    get_sheet_values,
    update_sheet_values,
    col_index_to_letter,
    get_sheet_data_with_hyperlinks as get_hyperlinks_util,
)
from urarovite.utils.google_api_backoff import (
    execute_with_backoff,
    READ_CONFIG,
    WRITE_CONFIG,
)


class GoogleSheetsSpreadsheet(SpreadsheetInterface):
    """Google Sheets implementation of SpreadsheetInterface."""

    def __init__(
        self, url: str, auth_credentials: Dict[str, Any], subject: Optional[str] = None
    ) -> None:
        """Initialize Google Sheets spreadsheet.

        Args:
            url: Google Sheets URL
            auth_credentials: Authentication credentials
            subject: Optional subject for domain-wide delegation

        Raises:
            ValidationError: If unable to initialize Google Sheets access
        """
        self.url = url
        self.spreadsheet_id = extract_sheet_id(url)

        if not self.spreadsheet_id:
            raise ValidationError(f"Invalid Google Sheets URL: {url}")

        # Extract encoded credentials from auth_credentials
        # Handle both direct base64 string and nested structure
        if isinstance(auth_credentials, str):
            encoded_creds = auth_credentials
        elif isinstance(auth_credentials, dict):
            encoded_creds = auth_credentials.get(
                "encoded_credentials"
            ) or auth_credentials.get("auth_secret")
            if not encoded_creds:
                raise ValidationError(
                    "No encoded credentials found in auth_credentials"
                )
        else:
            raise ValidationError("Invalid auth_credentials format")

        try:
            self.sheets_service = create_sheets_service_from_encoded_creds(
                encoded_creds, subject
            )
        except Exception as e:
            raise ValidationError(f"Failed to create Google Sheets service: {str(e)}")

        self._metadata: Optional[SpreadsheetMetadata] = None

    def get_metadata(self) -> SpreadsheetMetadata:
        """Get Google Sheets metadata with exponential backoff."""
        if self._metadata is None:
            try:
                # Get spreadsheet metadata with exponential backoff
                def _get_metadata():
                    return (
                        self.sheets_service.spreadsheets()
                        .get(spreadsheetId=self.spreadsheet_id)
                        .execute()
                    )

                spreadsheet_data = execute_with_backoff(
                    _get_metadata, config=READ_CONFIG
                )

                title = spreadsheet_data.get("properties", {}).get("title", "Untitled")
                sheets = spreadsheet_data.get("sheets", [])
                sheet_names = [sheet["properties"]["title"] for sheet in sheets]

                self._metadata = SpreadsheetMetadata(
                    spreadsheet_id=self.spreadsheet_id,
                    title=title,
                    sheet_names=sheet_names,
                    spreadsheet_type="google_sheets",
                    url=self.url,
                )

            except Exception as e:
                raise ValidationError(f"Failed to get Google Sheets metadata: {str(e)}")

        return self._metadata

    def get_sheet_data(
        self, sheet_name: Optional[str] = None, range_name: Optional[str] = None
    ) -> SheetData:
        """Get data from Google Sheets."""
        try:
            # Get sheet name if not provided
            if not sheet_name:
                metadata = self.get_metadata()
                if not metadata.sheet_names:
                    raise ValidationError("No sheets found in spreadsheet")
                sheet_name = metadata.sheet_names[0]

            # Construct range
            if range_name:
                # If range_name already includes sheet name, use as-is
                if "!" in range_name:
                    full_range = range_name
                else:
                    full_range = f"'{sheet_name}'!{range_name}"
            else:
                full_range = f"'{sheet_name}'"

            # Get data using existing utility
            result = get_sheet_values(
                self.sheets_service, self.spreadsheet_id, full_range
            )

            if not result["success"]:
                raise ValidationError(f"Failed to read sheet data: {result['error']}")

            return SheetData(
                values=result["values"],
                sheet_name=sheet_name,
                rows=result["rows"],
                cols=result["cols"],
            )

        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise ValidationError(f"Failed to get Google Sheets data: {str(e)}")

    def get_sheet_data_with_hyperlinks(
        self, sheet_name: Optional[str] = None, range_name: Optional[str] = None
    ) -> SheetData:
        """Get data from Google Sheets, resolving hyperlinks."""
        try:
            if not sheet_name:
                metadata = self.get_metadata()
                if not metadata.sheet_names:
                    raise ValidationError("No sheets found in spreadsheet")
                sheet_name = metadata.sheet_names[0]

            def _get_sheet_id_by_name(name: str) -> Optional[int]:
                # This requires fetching full metadata, which is inefficient.
                # A better approach would be to have sheet IDs in get_metadata()
                # For now, we fetch it here.
                spreadsheet_data = (
                    self.sheets_service.spreadsheets()
                    .get(spreadsheetId=self.spreadsheet_id, fields="sheets.properties")
                    .execute()
                )
                for sheet in spreadsheet_data.get("sheets", []):
                    if sheet.get("properties", {}).get("title") == name:
                        return sheet.get("properties", {}).get("sheetId")
                return None

            sheet_gid = _get_sheet_id_by_name(sheet_name)
            if sheet_gid is None:
                raise ValidationError(f"Sheet '{sheet_name}' not found.")

            values = get_hyperlinks_util(
                self.sheets_service, self.spreadsheet_id, sheet_name, sheet_gid
            )

            # Basic row/col calculation, can be enhanced
            rows = len(values)
            cols = max(len(row) for row in values) if values else 0

            return SheetData(values=values, sheet_name=sheet_name, rows=rows, cols=cols)

        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise ValidationError(f"Failed to get hyperlinks data: {str(e)}")

    def _extract_hyperlinks_from_values(
        self, values: List[List[Any]], sheet_name: str, range_name: str
    ) -> List[List[Any]]:
        """Extract hyperlink URLs and replace display text with actual URLs."""
        try:
            # Get cell formatting to extract hyperlinks
            # Use a more targeted approach to get just the hyperlink data
            spreadsheet_data = (
                self.sheets_service.spreadsheets()
                .get(
                    spreadsheetId=self.spreadsheet_id,
                    ranges=range_name,
                    fields="sheets(data(rowData(values(hyperlink,formattedValue))))",
                )
                .execute()
            )

            # Process the hyperlink data
            processed_values = []
            for row_idx, row in enumerate(values):
                processed_row = []
                for col_idx, cell_value in enumerate(row):
                    # Try to extract hyperlink URL
                    hyperlink_url = self._extract_hyperlink_url(
                        spreadsheet_data, row_idx, col_idx
                    )

                    if hyperlink_url:
                        processed_row.append(hyperlink_url)
                    else:
                        processed_row.append(cell_value)

                processed_values.append(processed_row)

            return processed_values

        except Exception:
            # If hyperlink extraction fails, return original values
            # This ensures backward compatibility
            return values

    def _extract_hyperlink_url(
        self, spreadsheet_data: Dict[str, Any], row_idx: int, col_idx: int
    ) -> Optional[str]:
        """Extract hyperlink URL from a specific cell."""
        try:
            sheets = spreadsheet_data.get("sheets", [])
            if not sheets:
                return None

            sheet_data = sheets[0].get("data", [])
            if not sheet_data:
                return None

            row_data = sheet_data[0].get("rowData", [])
            if row_idx >= len(row_data):
                return None

            row = row_data[row_idx]
            if not row or "values" not in row:
                return None

            values = row["values"]
            if col_idx >= len(values):
                return None

            cell = values[col_idx]
            if not cell or "hyperlink" not in cell:
                return None

            hyperlink = cell["hyperlink"]
            if isinstance(hyperlink, str):
                return hyperlink
            elif isinstance(hyperlink, dict):
                return hyperlink.get("url") or hyperlink.get("linkUri")

            return None

        except Exception:
            # If anything goes wrong, return None (no hyperlink)
            return None

    def update_sheet_data(
        self,
        sheet_name: str,
        values: List[List[Any]],
        start_row: int = 1,
        start_col: int = 1,
        range_name: Optional[str] = None,
    ) -> None:
        """Update data in Google Sheets."""
        try:
            if range_name:
                # Use provided range
                if "!" not in range_name:
                    full_range = f"'{sheet_name}'!{range_name}"
                else:
                    full_range = range_name
            else:
                # Construct range from start position and data dimensions
                start_col_letter = col_index_to_letter(start_col - 1)
                end_row = start_row + len(values) - 1
                end_col_letter = (
                    col_index_to_letter(start_col + len(values[0]) - 2)
                    if values and values[0]
                    else start_col_letter
                )

                full_range = f"'{sheet_name}'!{start_col_letter}{start_row}:{end_col_letter}{end_row}"

            # Update using existing utility
            result = update_sheet_values(
                self.sheets_service, self.spreadsheet_id, full_range, values
            )

            if not result["success"]:
                raise ValidationError(f"Failed to update sheet: {result['error']}")

        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise ValidationError(f"Failed to update Google Sheets data: {str(e)}")

    def update_sheet_properties(
        self, sheet_name: str, new_name: Optional[str] = None, **properties: Any
    ) -> None:
        """Update Google Sheets properties with exponential backoff."""
        try:
            # Get sheet ID from metadata with exponential backoff
            def _get_sheet_metadata():
                return (
                    self.sheets_service.spreadsheets()
                    .get(spreadsheetId=self.spreadsheet_id)
                    .execute()
                )

            spreadsheet_data = execute_with_backoff(
                _get_sheet_metadata, config=READ_CONFIG
            )

            # Find the sheet ID
            sheet_id = None
            for sheet in spreadsheet_data.get("sheets", []):
                if sheet["properties"]["title"] == sheet_name:
                    sheet_id = sheet["properties"]["sheetId"]
                    break

            if sheet_id is None:
                raise ValidationError(f"Sheet '{sheet_name}' not found")

            # Prepare update request
            requests = []

            if new_name:
                requests.append(
                    {
                        "updateSheetProperties": {
                            "properties": {
                                "sheetId": sheet_id,
                                "title": new_name,
                            },
                            "fields": "title",
                        }
                    }
                )

            # Add other property updates if needed
            for prop_name, prop_value in properties.items():
                if prop_name != "title":  # title handled above
                    requests.append(
                        {
                            "updateSheetProperties": {
                                "properties": {
                                    "sheetId": sheet_id,
                                    prop_name: prop_value,
                                },
                                "fields": prop_name,
                            }
                        }
                    )

            if requests:
                body = {"requests": requests}

                # Execute batch update with exponential backoff
                def _batch_update():
                    return (
                        self.sheets_service.spreadsheets()
                        .batchUpdate(spreadsheetId=self.spreadsheet_id, body=body)
                        .execute()
                    )

                execute_with_backoff(_batch_update, config=WRITE_CONFIG)

                # Invalidate cached metadata
                self._metadata = None

        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise ValidationError(
                f"Failed to update Google Sheets properties: {str(e)}"
            )

    def create_sheet(self, sheet_name: str) -> None:
        """Create a new sheet in Google Sheets with exponential backoff."""
        try:
            requests = [{"addSheet": {"properties": {"title": sheet_name}}}]

            body = {"requests": requests}

            # Execute batch update with exponential backoff
            def _create_sheet():
                return (
                    self.sheets_service.spreadsheets()
                    .batchUpdate(spreadsheetId=self.spreadsheet_id, body=body)
                    .execute()
                )

            execute_with_backoff(_create_sheet, config=WRITE_CONFIG)

            # Invalidate cached metadata
            self._metadata = None

        except Exception as e:
            raise ValidationError(f"Failed to create Google Sheets sheet: {str(e)}")

    def delete_sheet(self, sheet_name: str) -> None:
        """Delete a sheet from Google Sheets with exponential backoff."""
        try:
            # Get sheet ID with exponential backoff
            def _get_sheet_data():
                return (
                    self.sheets_service.spreadsheets()
                    .get(spreadsheetId=self.spreadsheet_id)
                    .execute()
                )

            spreadsheet_data = execute_with_backoff(_get_sheet_data, config=READ_CONFIG)

            sheet_id = None
            for sheet in spreadsheet_data.get("sheets", []):
                if sheet["properties"]["title"] == sheet_name:
                    sheet_id = sheet["properties"]["sheetId"]
                    break

            if sheet_id is None:
                raise ValidationError(f"Sheet '{sheet_name}' not found")

            requests = [{"deleteSheet": {"sheetId": sheet_id}}]

            body = {"requests": requests}

            # Execute batch update with exponential backoff
            def _delete_sheet():
                return (
                    self.sheets_service.spreadsheets()
                    .batchUpdate(spreadsheetId=self.spreadsheet_id, body=body)
                    .execute()
                )

            execute_with_backoff(_delete_sheet, config=WRITE_CONFIG)

            # Invalidate cached metadata
            self._metadata = None

        except Exception as e:
            raise ValidationError(f"Failed to delete Google Sheets sheet: {str(e)}")

    def save(self) -> None:
        """Save changes (no-op for Google Sheets as changes are auto-saved)."""
        pass

    def close(self) -> None:
        """Close Google Sheets connection (cleanup if needed)."""
        # Google Sheets API doesn't require explicit closing
        # But we can clear cached data
        self._metadata = None

    def get_formulas(
        self, sheet_name: Optional[str] = None
    ) -> Dict[str, Dict[str, str]]:
        """Get formulas from Google Sheets.

        Args:
            sheet_name: Name of specific sheet (optional, gets all sheets if None)

        Returns:
            Dict mapping sheet names to dict of cell coordinates to formulas
        """
        try:
            from urarovite.utils.sheets import fetch_workbook_with_formulas

            return fetch_workbook_with_formulas(
                self.sheets_service, self.spreadsheet_id
            )
        except Exception as e:
            raise ValidationError(
                f"Failed to read formulas from Google Sheets: {str(e)}"
            )

    def update_sheet_formulas(
        self, sheet_name: str, formulas: Dict[str, str], preserve_values: bool = True
    ) -> None:
        """Update formulas in Google Sheets.

        Args:
            sheet_name: Name of the sheet to update
            formulas: Dict mapping cell coordinates to formulas
            preserve_values: Whether to preserve existing values for non-formula cells
        """
        if not formulas:
            return

        try:
            # Get sheet ID for the sheet name
            metadata = self.get_metadata()
            for sheet_info in metadata.sheet_names:
                if sheet_info == sheet_name:
                    # We need to get the actual sheet ID, not just the name
                    # For now, we'll use the sheet name and let the API handle it
                    break

            # Prepare batch update requests for formulas
            requests = []

            for cell_ref, formula in formulas.items():
                try:
                    # Ensure formula starts with =
                    if not formula.startswith("="):
                        formula = "=" + formula

                    # Parse cell reference to get row and column
                    import re

                    match = re.match(r"^([A-Z]+)(\d+)$", cell_ref.upper())
                    if not match:
                        import logging

                        logging.warning(f"Invalid cell reference: {cell_ref}")
                        continue

                    col_letters, row_str = match.groups()
                    row_index = int(row_str) - 1  # Convert to 0-based

                    # Convert column letters to index
                    col_index = 0
                    for i, char in enumerate(reversed(col_letters)):
                        col_index += (ord(char) - ord("A") + 1) * (26**i)
                    col_index -= 1  # Convert to 0-based

                    # Create update request
                    requests.append(
                        {
                            "updateCells": {
                                "range": {
                                    "sheetId": 0,  # TODO: Get actual sheet ID
                                    "startRowIndex": row_index,
                                    "endRowIndex": row_index + 1,
                                    "startColumnIndex": col_index,
                                    "endColumnIndex": col_index + 1,
                                },
                                "rows": [
                                    {
                                        "values": [
                                            {
                                                "userEnteredValue": {
                                                    "formulaValue": formula
                                                }
                                            }
                                        ]
                                    }
                                ],
                                "fields": "userEnteredValue",
                            }
                        }
                    )

                except Exception as e:
                    import logging

                    logging.warning(
                        f"Failed to prepare formula update for cell {cell_ref}: {formula}. Error: {e}"
                    )

            if requests:
                # Execute batch update with exponential backoff
                body = {"requests": requests}

                def _update_formulas():
                    return (
                        self.sheets_service.spreadsheets()
                        .batchUpdate(spreadsheetId=self.spreadsheet_id, body=body)
                        .execute()
                    )

                execute_with_backoff(_update_formulas, config=WRITE_CONFIG)

        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise ValidationError(f"Failed to update Google Sheets formulas: {str(e)}")
