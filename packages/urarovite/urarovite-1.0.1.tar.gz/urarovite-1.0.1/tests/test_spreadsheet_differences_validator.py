"""Tests for SpreadsheetDifferencesValidator."""

from unittest.mock import Mock, patch

from urarovite.validators.spreadsheet_differences import (
    SpreadsheetDifferencesValidator,
    run,
)


class TestSpreadsheetDifferencesValidator:
    def setup_method(self):
        self.validator = SpreadsheetDifferencesValidator()

    @patch("urarovite.validators.spreadsheet_differences.fetch_workbook")
    def test_validate_identical_workbooks(self, mock_fetch):
        """
        Test that the validator returns no issues when the input and output spreadsheets are identical.
        """
        wb = {
            "properties": {"title": "Same"},
            "sheets": [
                {"properties": {"title": "Tab"}, "data": {"rowData": [{"values": [{"effectiveValue": {"numberValue": 1}}]}]}},
            ],
        }
        mock_fetch.side_effect = [wb, wb]

        mock_service = Mock()
        input_url = "https://docs.google.com/spreadsheets/d/input123/edit"
        output_url = "https://docs.google.com/spreadsheets/d/output456/edit"

        result = self.validator.validate(
            sheets_service=mock_service,
            sheet_id="",
            mode="flag",
            input_sheet_url=input_url,
            output_sheet_url=output_url,
        )

        assert result["issues_found"] == 0
        assert result["errors"] == []
        assert result["details"]["equal"] is True
        assert result["details"]["input_hash"] == result["details"]["output_hash"]
        assert result["automated_log"] == "No issues found"

    @patch("urarovite.validators.spreadsheet_differences.fetch_workbook")
    def test_validate_different_workbooks(self, mock_fetch):
        """
        Test that the validator returns an issue when the input and output spreadsheets are different.
        """
        wb1 = {"properties": {"title": "A"}, "sheets": []}
        wb2 = {"properties": {"title": "B"}, "sheets": []}
        mock_fetch.side_effect = [wb1, wb2]

        mock_service = Mock()
        input_url = "https://docs.google.com/spreadsheets/d/input123/edit"
        output_url = "https://docs.google.com/spreadsheets/d/output456/edit"

        result = self.validator.validate(
            sheets_service=mock_service,
            sheet_id="",
            mode="flag",
            input_sheet_url=input_url,
            output_sheet_url=output_url,
        )

        assert result["issues_found"] == 1
        assert result["errors"] == []
        assert result["details"]["equal"] is False
        assert result["details"]["input_hash"] != result["details"]["output_hash"]
        assert result["automated_log"] == "Content differs"

    def test_validate_missing_urls(self):
        """
        Test that the validator returns an issue when the input and output spreadsheets are missing.
        """
        mock_service = Mock()

        result = self.validator.validate(
            sheets_service=mock_service,
            sheet_id="",
            mode="flag",
            input_sheet_url=None,
            output_sheet_url=None,
        )

        assert len(result["errors"]) == 1
        assert "Missing spreadsheet URLs" in result["errors"][0]
        assert result["automated_log"] == "No issues found"


    @patch("urarovite.validators.spreadsheet_differences.fetch_workbook")
    def test_validate_unexpected_error(self, mock_fetch):
        """
        Test that the validator returns an issue when an unexpected error occurs.
        """
        mock_fetch.side_effect = RuntimeError("Boom")

        mock_service = Mock()
        input_url = "https://docs.google.com/spreadsheets/d/input123/edit"
        output_url = "https://docs.google.com/spreadsheets/d/output456/edit"

        result = self.validator.validate(
            sheets_service=mock_service,
            sheet_id="",
            mode="flag",
            input_sheet_url=input_url,
            output_sheet_url=output_url,
        )

        assert any("Unexpected error: Boom" in e for e in result["errors"]) 
        assert result["automated_log"] == "No issues found"


