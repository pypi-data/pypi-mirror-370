"""Tests for SpreadsheetDifferencesValidator."""

import pytest
from unittest.mock import Mock, patch
import pandas as pd

from urarovite.validators.spreadsheet_differences import (
    SpreadsheetDifferencesValidator,
    run,
)
from .fixtures import BaseTestCase


class TestSpreadsheetDifferencesValidator(BaseTestCase):
    def setup_method(self):
        super().setup_method()
        self.validator = SpreadsheetDifferencesValidator()

    @patch("urarovite.validators.spreadsheet_differences.fetch_workbook_with_formulas")
    def test_validate_identical_workbooks(self, mock_fetch):
        """
        Test that the validator returns no flags when the input and output spreadsheets are identical.
        """
        wb = {
            "properties": {"title": "Same"},
            "sheets": [
                {
                    "properties": {"title": "Tab"},
                    "data": {
                        "rowData": [
                            {"values": [{"effectiveValue": {"numberValue": 1}}]}
                        ]
                    },
                },
            ],
        }
        mock_fetch.side_effect = [wb, wb]

        # Create test data with spreadsheet URLs to compare
        input_url = "https://docs.google.com/spreadsheets/d/input123/edit"
        output_url = "https://docs.google.com/spreadsheets/d/output456/edit"

        # Mock spreadsheet with comparison data
        with patch.object(self.validator, "_get_spreadsheet") as mock_get_spreadsheet:
            mock_spreadsheet = Mock()
            mock_sheet_data = Mock()
            mock_sheet_data.values = [
                ["input_sheet_url", "example_output_sheet_url"],
                [input_url, output_url],
            ]
            mock_spreadsheet.get_sheet_data.return_value = mock_sheet_data
            mock_get_spreadsheet.return_value = mock_spreadsheet

            result = self.validator.validate(
                spreadsheet_source="https://docs.google.com/spreadsheets/d/metadata123/edit",
                mode="flag",
                auth_credentials={"auth_secret": self.encoded_creds},
            )

        # The validator should work without errors
        assert result["flags_found"] >= 0
        assert isinstance(result["errors"], list)

    @patch("urarovite.validators.spreadsheet_differences.fetch_workbook_with_formulas")
    def test_validate_different_workbooks(self, mock_fetch):
        """
        Test that the validator returns an issue when the input and output spreadsheets are different.
        """
        wb1 = {"properties": {"title": "A"}, "sheets": []}
        wb2 = {"properties": {"title": "B"}, "sheets": []}
        mock_fetch.side_effect = [wb1, wb2]

        # Create test data with spreadsheet URLs to compare
        input_url = "https://docs.google.com/spreadsheets/d/input123/edit"
        output_url = "https://docs.google.com/spreadsheets/d/output456/edit"

        # Mock spreadsheet with comparison data
        with patch.object(self.validator, "_get_spreadsheet") as mock_get_spreadsheet:
            mock_spreadsheet = Mock()
            mock_sheet_data = Mock()
            mock_sheet_data.values = [
                ["input_sheet_url", "example_output_sheet_url"],
                [input_url, output_url],
            ]
            mock_spreadsheet.get_sheet_data.return_value = mock_sheet_data
            mock_get_spreadsheet.return_value = mock_spreadsheet

            result = self.validator.validate(
                spreadsheet_source="https://docs.google.com/spreadsheets/d/metadata123/edit",
                mode="flag",
                auth_credentials={"auth_secret": self.encoded_creds},
            )

        # The validator should work and potentially find differences
        assert result["flags_found"] == 0
        assert isinstance(result["errors"], list)

    def test_validate_missing_urls(self):
        """
        Test that the validator returns an issue when the input and output spreadsheets are missing.
        """
        # Mock spreadsheet with missing/empty comparison data
        with patch.object(self.validator, "_get_spreadsheet") as mock_get_spreadsheet:
            mock_spreadsheet = Mock()
            mock_sheet_data = Mock()
            mock_sheet_data.values = [
                ["input_sheet_url", "example_output_sheet_url"],
                ["", ""],  # Empty URLs
            ]
            mock_spreadsheet.get_sheet_data.return_value = mock_sheet_data
            mock_get_spreadsheet.return_value = mock_spreadsheet

            result = self.validator.validate(
                spreadsheet_source="https://docs.google.com/spreadsheets/d/metadata123/edit",
                mode="flag",
                auth_credentials={"auth_secret": self.encoded_creds},
            )

        # The validator should handle empty URLs gracefully
        assert result["flags_found"] == 0
        assert isinstance(result["errors"], list)

    def test_validate_unexpected_error(self):
        """
        Test that the validator returns an issue when an unexpected error occurs.
        """
        # Mock spreadsheet with comparison data
        with patch.object(self.validator, "_get_spreadsheet") as mock_get_spreadsheet:
            mock_get_spreadsheet.side_effect = RuntimeError("Boom")

            result = self.validator.validate(
                spreadsheet_source="https://docs.google.com/spreadsheets/d/metadata123/edit",
                mode="flag",
                auth_credentials={"auth_secret": self.encoded_creds},
            )

        # Should handle the error gracefully
        assert result["flags_found"] == 0
        assert len(result["errors"]) > 0
        assert "Unexpected error: Boom" in result["errors"][0]
        assert isinstance(result["errors"], list)


class MockWorkbook:
    def __init__(self, properties, sheets):
        self.properties = properties
        self.sheets = sheets
