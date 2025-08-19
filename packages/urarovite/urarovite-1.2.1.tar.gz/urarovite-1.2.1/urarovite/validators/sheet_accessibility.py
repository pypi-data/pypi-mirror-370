"""Sheet accessibility validator for Google Sheets URLs.

This validator checks whether Google Sheets URLs are accessible using
the spreadsheet abstraction layer.
"""

import re
from typing import Any, Dict, List, Union
from pathlib import Path

from urarovite.validators.base import BaseValidator, ValidationResult
from urarovite.core.exceptions import ValidationError
from urarovite.core.spreadsheet import SpreadsheetInterface, SpreadsheetFactory


class SheetAccessibilityValidator(BaseValidator):
    """Validator for checking Google Sheets URL accessibility."""

    # Regex to extract spreadsheet ID from Google Sheets URLs
    _ID_RE = re.compile(r"/d/([a-zA-Z0-9-_]+)")

    def __init__(self) -> None:
        super().__init__(
            validator_id="sheet_accessibility",
            name="Check Sheet Accessibility",
            description="Validates that Google Sheets URLs are accessible",
        )

    def validate(
        self,
        spreadsheet_source: Union[str, Path, SpreadsheetInterface],
        mode: str,
        auth_credentials: Dict[str, Any] = None,
        url_columns: List[int] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Validate Google Sheets URL accessibility.

        Args:
            spreadsheet_source: Either a Google Sheets URL, Excel file path,
                or SpreadsheetInterface
            mode: Either "fix" (not applicable) or "flag" (report only)
            auth_credentials: Authentication credentials (required for Google Sheets)
            url_columns: List of 1-based column indices containing URLs

        Returns:
            Dict with validation results
        """

        def validation_logic(
            spreadsheet: SpreadsheetInterface, result: ValidationResult, **kwargs
        ) -> None:
            # Get all sheet data
            data, sheet_name = self._get_all_sheet_data(spreadsheet)

            if not data:
                result.add_error("Sheet is empty - no data to validate")
                result.details["accessible_count"] = 0
                result.details["inaccessible_urls"] = []
                result.set_automated_log("Sheet is empty - no data to validate")
                return

            # Auto-detect URL columns if not specified
            detected_url_columns = url_columns
            if detected_url_columns is None:
                detected_url_columns = self._detect_url_columns(data)
                if not detected_url_columns:
                    # Return empty result instead of error
                    result.details["message"] = "No Google Sheets URLs found in data"
                    result.details["accessible_count"] = 0
                    result.details["inaccessible_urls"] = []
                    return

            # Get auth credentials for URL checking
            auth_secret = None
            subject = None

            if auth_credentials:
                auth_secret = auth_credentials.get(
                    "auth_secret"
                ) or auth_credentials.get("encoded_credentials")
                subject = auth_credentials.get("subject")

            if not auth_secret:
                # Return empty result instead of error
                result.details["message"] = "Authentication credentials not provided"
                result.details["accessible_count"] = 0
                result.details["inaccessible_urls"] = []
                return

            accessible_count = 0

            # Check each URL in the specified columns
            for row_idx, row in enumerate(data):
                if row_idx == 0:  # Skip header row
                    continue

                for col_idx in detected_url_columns:
                    if col_idx <= len(row):
                        url = row[col_idx - 1]  # Convert to 0-based index
                        if url and isinstance(url, str):
                            accessibility_result = self._check_url_accessibility(
                                url, auth_secret, subject
                            )

                            if not accessibility_result["accessible"]:
                                cell_ref = self._generate_cell_reference(
                                    row_idx - 1, col_idx - 1, sheet_name
                                )
                                result.add_detailed_issue(
                                    sheet_name=sheet_name,
                                    cell=cell_ref,
                                    message=f"Inaccessible URL: {accessibility_result['error']}",
                                    value=url,
                                )
                            else:
                                accessible_count += 1

            # Record results
            if result.flags_found > 0:
                result.set_automated_log(
                    f"Found {result.flags_found} inaccessible URLs."
                )
            else:
                result.set_automated_log("All URLs are accessible.")

        return self._execute_validation(
            validation_logic, spreadsheet_source, auth_credentials, **kwargs
        )

    def _detect_url_columns(self, data: List[List[Any]]) -> List[int]:
        """Auto-detect columns containing Google Sheets URLs."""
        url_columns = []

        if not data:
            return url_columns

        # Check first few rows for URLs
        sample_rows = data[: min(5, len(data))]

        for col_idx in range(len(data[0]) if data[0] else 0):
            contains_urls = False

            for row in sample_rows:
                if col_idx < len(row) and row[col_idx]:
                    cell_value = str(row[col_idx])
                    if "docs.google.com/spreadsheets" in cell_value:
                        contains_urls = True
                        break

            if contains_urls:
                url_columns.append(col_idx + 1)  # Convert to 1-based

        return url_columns

    def _extract_sheet_id(self, url: str) -> str | None:
        """Extract spreadsheet ID from Google Sheets URL."""
        if not url:
            return None
        match = self._ID_RE.search(url)
        return match.group(1) if match else None

    def _check_url_accessibility(
        self, url: str, auth_secret: str, subject: str | None = None
    ) -> Dict[str, Any]:
        """Check if a Google Sheets URL is accessible."""
        if not url or "docs.google.com" not in url:
            return {"accessible": False, "error": "invalid_url_format"}

        try:
            # Create auth credentials dict
            auth_credentials = {"auth_secret": auth_secret}
            if subject:
                auth_credentials["subject"] = subject

            # Try to create spreadsheet interface
            spreadsheet = SpreadsheetFactory.create_spreadsheet(url, auth_credentials)

            try:
                # Try to access basic metadata to verify accessibility
                metadata = spreadsheet.get_metadata()
                _ = metadata.title  # Access title to verify we can read the spreadsheet

                return {"accessible": True, "error": None}

            finally:
                spreadsheet.close()

        except Exception as e:
            error_msg = str(e)
            if "403" in error_msg or "Forbidden" in error_msg:
                error_type = "forbidden"
            elif "404" in error_msg or "not found" in error_msg.lower():
                error_type = "not_found"
            else:
                error_type = f"request_exception:{e.__class__.__name__}"

            return {"accessible": False, "error": error_type}
