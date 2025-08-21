"""Test suite for EmptyInvalidRangesValidator using built-in unittest.

This script runs EmptyInvalidRangesValidator tests without requiring external dependencies.
"""

import sys
import unittest
from unittest.mock import Mock, patch, MagicMock
import os

# Add the project root to the path so we can import urarovite modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from urarovite.validators.empty_invalid_ranges import EmptyInvalidRangesValidator
    from urarovite.core.exceptions import ValidationError
except ImportError as e:
    print(f"❌ Failed to import modules: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)


class TestEmptyInvalidRangesValidator(unittest.TestCase):
    """Test suite for EmptyInvalidRangesValidator using unittest."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.validator = EmptyInvalidRangesValidator()
        self.mock_sheets_service = Mock()

    def test_validator_initialization(self):
        """Test that the validator is properly initialized."""
        self.assertEqual(self.validator.id, "empty_invalid_ranges")
        self.assertEqual(self.validator.name, "Check Empty and Invalid Ranges")
        self.assertIn("A1 ranges", self.validator.description)

    def test_col_to_num(self):
        """Test column letter to number conversion."""
        test_cases = [
            ("A", 1),
            ("B", 2),
            ("Z", 26),
            ("AA", 27),
            ("AB", 28),
            ("AZ", 52),
            ("BA", 53),
        ]

        for col, expected in test_cases:
            with self.subTest(col=col):
                result = self.validator._col_to_num(col)
                self.assertEqual(result, expected)

    def test_col_to_num_invalid(self):
        """Test column letter to number conversion with invalid input."""
        invalid_cases = ["1", "A1", "!"]

        for col in invalid_cases:
            with self.subTest(col=col):
                result = self.validator._col_to_num(col)
                self.assertEqual(result, -1)

    def test_zero_sized_ranges(self):
        """Test detection of zero-sized or invalid ranges."""
        # Valid ranges (should return False)
        valid_ranges = [
            "A1:B2",
            "A1:A10",
            "A:B",
            "1:5",
            "A1",
        ]

        for range_str in valid_ranges:
            with self.subTest(range_str=range_str):
                result = self.validator._zero_sized(range_str)
                self.assertFalse(result, f"Should be valid: {range_str}")

        # Invalid ranges (should return True)
        invalid_ranges = [
            "B1:A1",  # Reversed columns
            "A2:A1",  # Reversed rows
            "A0:A1",  # Invalid row
            "0:1",  # Invalid row range
        ]

        for range_str in invalid_ranges:
            with self.subTest(range_str=range_str):
                result = self.validator._zero_sized(range_str)
                self.assertTrue(result, f"Should be invalid: {range_str}")

    def test_extract_spreadsheet_id(self):
        """Test spreadsheet ID extraction from URLs using the utility function."""
        from urarovite.utils.sheets import extract_sheet_id

        test_cases = [
            (
                "https://docs.google.com/spreadsheets/d/1E7RF7lBnVAEIVB7NoF24l4vBoV-t7VMRdrsAWHHU4YQ/",
                "1E7RF7lBnVAEIVB7NoF24l4vBoV-t7VMRdrsAWHHU4YQ",
            ),
            ("http://docs.google.com/spreadsheets/d/abc123def456/edit", "abc123def456"),
            ("invalid_url", None),
            ("", None),
            (None, None),
        ]

        for url, expected in test_cases:
            with self.subTest(url=url):
                result = extract_sheet_id(url)
                self.assertEqual(result, expected)

    def test_detect_range_columns(self):
        """Test auto-detection of columns containing A1 ranges."""
        # Sample data with ranges in column 2
        data = [
            ["Header1", "Range", "Header3"],
            ["Data1", "Sheet1!A1:B10", "Data3"],
            ["Data4", "Sheet2!C5:D15", "Data6"],
        ]

        result = self.validator._detect_range_columns(data)
        self.assertEqual(result, [2])  # 1-based column index

    def test_detect_range_columns_multiple(self):
        """Test detection of multiple range columns."""
        data = [
            ["Header1", "Range1", "Header3", "Range2"],
            ["Data1", "Sheet1!A1:B10", "Data3", "Sheet2!X1:Y5"],
            ["Data4", "Sheet1!C5:D15", "Data6", "Sheet2!Z10:AA20"],
        ]

        result = self.validator._detect_range_columns(data)
        self.assertEqual(sorted(result), [2, 4])

    def test_detect_url_columns(self):
        """Test auto-detection of columns containing Google Sheets URLs."""
        data = [
            ["Header1", "URL", "Header3"],
            ["Data1", "https://docs.google.com/spreadsheets/d/abc123/", "Data3"],
            ["Data4", "https://docs.google.com/spreadsheets/d/def456/", "Data6"],
        ]

        result = self.validator._detect_url_columns(data)
        self.assertEqual(result, [2])

    def test_detect_columns_empty_data(self):
        """Test column detection with empty data."""
        self.assertEqual(self.validator._detect_range_columns([]), [])
        self.assertEqual(self.validator._detect_url_columns([]), [])

    @patch("urarovite.validators.empty_invalid_ranges.get_sheet_values")
    def test_validate_sheet_range_valid(self, mock_get_values):
        """Test validation of a valid, non-empty range."""
        # Mock the utility function response
        mock_get_values.return_value = {
            "success": True,
            "values": [["data1", "data2"], ["data3", "data4"]],
            "error": None,
        }

        result = self.validator._validate_sheet_range(
            self.mock_sheets_service,
            "Sheet1!A1:B2",
            "https://docs.google.com/spreadsheets/d/test123/",
        )

        self.assertTrue(result[0])
        self.assertEqual(result[1], "Range is valid and not empty")

    @patch("urarovite.validators.empty_invalid_ranges.get_sheet_values")
    def test_validate_sheet_range_empty(self, mock_get_values):
        """Test validation of an empty range."""
        mock_get_values.return_value = {
            "success": True,
            "values": [["", ""], ["", ""]],
            "error": None,
        }

        result = self.validator._validate_sheet_range(
            self.mock_sheets_service,
            "Sheet1!A1:B2",
            "https://docs.google.com/spreadsheets/d/test123/",
        )

        self.assertFalse(result[0])
        self.assertIn("empty", result[1])

    def test_validate_sheet_range_invalid_url(self):
        """Test validation with invalid URL."""
        result = self.validator._validate_sheet_range(
            self.mock_sheets_service, "Sheet1!A1:B2", "invalid_url"
        )

        self.assertFalse(result[0])
        self.assertIn("Invalid spreadsheet URL", result[1])

    def test_validate_sheet_range_invalid_range(self):
        """Test validation with invalid range."""
        result = self.validator._validate_sheet_range(
            self.mock_sheets_service,
            "",
            "https://docs.google.com/spreadsheets/d/test123/",
        )

        self.assertFalse(result[0])
        self.assertIn("Range is missing", result[1])

    def test_validate_sheet_range_zero_sized(self):
        """Test validation with zero-sized range."""
        result = self.validator._validate_sheet_range(
            self.mock_sheets_service,
            "Sheet1!B1:A1",  # Invalid reversed range
            "https://docs.google.com/spreadsheets/d/test123/",
        )

        self.assertFalse(result[0])
        self.assertIn("invalid or 0-sized", result[1])

    @patch("urarovite.validators.empty_invalid_ranges.get_sheet_values")
    def test_validate_sheet_range_http_error_403(self, mock_get_values):
        """Test validation with 403 HTTP error."""
        mock_get_values.return_value = {
            "success": False,
            "values": [],
            "error": "forbidden_or_not_found",
        }

        result = self.validator._validate_sheet_range(
            self.mock_sheets_service,
            "Sheet1!A1:B2",
            "https://docs.google.com/spreadsheets/d/test123/",
        )

        self.assertFalse(result[0])
        self.assertIn("No access", result[1])

    @patch("urarovite.validators.empty_invalid_ranges.get_sheet_values")
    def test_validate_sheet_range_http_error_404(self, mock_get_values):
        """Test validation with 404 HTTP error."""
        mock_get_values.return_value = {
            "success": False,
            "values": [],
            "error": "forbidden_or_not_found",
        }

        result = self.validator._validate_sheet_range(
            self.mock_sheets_service,
            "Sheet1!A1:B2",
            "https://docs.google.com/spreadsheets/d/test123/",
        )

        self.assertFalse(result[0])
        self.assertIn("not found", result[1])

    @patch("urarovite.utils.sheets.get_sheet_values")
    def test_validate_sheet_range_http_error_400(self, mock_get_values):
        """Test validation with 400 HTTP error."""
        mock_get_values.return_value = {
            "success": False,
            "values": [],
            "error": "request_exception:HttpError",
        }

        result = self.validator._validate_sheet_range(
            self.mock_sheets_service,
            "Sheet1!A1:B2",
            "https://docs.google.com/spreadsheets/d/test123/",
        )

        self.assertFalse(result[0])
        self.assertIn("Google Sheets API error", result[1])

    @patch.object(EmptyInvalidRangesValidator, "_get_spreadsheet")
    def test_validate_with_empty_sheet(self, mock_get_spreadsheet):
        """Test validate method with empty sheet."""
        # Mock spreadsheet
        mock_spreadsheet = Mock()
        mock_get_spreadsheet.return_value = mock_spreadsheet

        with patch.object(
            self.validator, "_get_all_sheet_data", return_value=([], "Sheet1")
        ):
            result = self.validator.validate(
                spreadsheet_source="https://docs.google.com/spreadsheets/d/test_id/edit",
                mode="flag",
                auth_credentials={"encoded_credentials": "fake_creds"},
            )

        self.assertIn("Sheet is empty", result["automated_log"])

    @patch.object(EmptyInvalidRangesValidator, "_get_spreadsheet")
    def test_validate_no_columns_detected(self, mock_get_spreadsheet):
        """Test validate method when no range or URL columns are detected."""
        test_data = [
            ["Header1", "Header2", "Header3"],
            ["Data1", "Data2", "Data3"],
        ]

        # Mock spreadsheet
        mock_spreadsheet = Mock()
        mock_get_spreadsheet.return_value = mock_spreadsheet

        with patch.object(
            self.validator, "_get_all_sheet_data", return_value=(test_data, "Sheet1")
        ):
            result = self.validator.validate(
                spreadsheet_source="https://docs.google.com/spreadsheets/d/test_id/edit",
                mode="flag",
                auth_credentials={"encoded_credentials": "fake_creds"},
            )

        self.assertEqual(result["automated_log"], "No range or URL columns detected")

    @patch.object(EmptyInvalidRangesValidator, "_get_spreadsheet")
    def test_validate_successful_validation(self, mock_get_spreadsheet):
        """Test validate method with successful validation."""
        test_data = [
            ["Range", "URL"],
            ["Sheet1!A1:B2", "https://docs.google.com/spreadsheets/d/test123/"],
        ]

        # Mock spreadsheet
        mock_spreadsheet = Mock()
        mock_get_spreadsheet.return_value = mock_spreadsheet

        with patch.object(
            self.validator, "_get_all_sheet_data", return_value=(test_data, "Sheet1")
        ):
            with patch.object(self.validator, "_create_sheets_service"):
                with patch.object(
                    self.validator,
                    "_validate_sheet_range",
                    return_value=(True, "Range is valid and not empty"),
                ):
                    result = self.validator.validate(
                        spreadsheet_source="https://docs.google.com/spreadsheets/d/test_id/edit",
                        mode="flag",
                        auth_credentials={"encoded_credentials": "fake_creds"},
                        range_columns=[1],
                        url_columns=[2],
                    )

        self.assertEqual(result["automated_log"], "All ranges are valid and non-empty.")

    @patch.object(EmptyInvalidRangesValidator, "_get_spreadsheet")
    def test_validate_with_invalid_ranges(self, mock_get_spreadsheet):
        """Test validate method with invalid ranges."""
        test_data = [
            ["Range", "URL"],
            ["Sheet1!A1:B2", "https://docs.google.com/spreadsheets/d/test123/"],
            ["InvalidRange", "https://docs.google.com/spreadsheets/d/test456/"],
        ]

        # Mock spreadsheet
        mock_spreadsheet = Mock()
        mock_get_spreadsheet.return_value = mock_spreadsheet

        def mock_validate_range(service, range_val, url_val, **kwargs):
            if range_val == "Sheet1!A1:B2":
                return (True, "Range is valid and not empty")
            else:
                return (False, "Range is empty — manual fix required")

        with patch.object(
            self.validator, "_get_all_sheet_data", return_value=(test_data, "Sheet1")
        ):
            with patch.object(self.validator, "_create_sheets_service"):
                with patch.object(
                    self.validator,
                    "_validate_sheet_range",
                    side_effect=mock_validate_range,
                ):
                    result = self.validator.validate(
                        spreadsheet_source="https://docs.google.com/spreadsheets/d/test_id/edit",
                        mode="flag",
                        auth_credentials={"encoded_credentials": "fake_creds"},
                        range_columns=[1],
                        url_columns=[2],
                    )

        self.assertEqual(result["flags_found"], 1)
        self.assertEqual(len(result["details"]["flags"]), 1)
        self.assertEqual(result["details"]["flags"][0]["value"], "InvalidRange")
        self.assertIn("empty or invalid ranges", result["automated_log"])

    @patch.object(EmptyInvalidRangesValidator, "_get_spreadsheet")
    def test_validate_with_exception(self, mock_get_spreadsheet):
        """Test validate method when an exception occurs."""
        # Mock spreadsheet
        mock_spreadsheet = Mock()
        mock_get_spreadsheet.return_value = mock_spreadsheet

        with patch.object(
            self.validator, "_get_all_sheet_data", side_effect=Exception("Test error")
        ):
            result = self.validator.validate(
                spreadsheet_source="https://docs.google.com/spreadsheets/d/test_id/edit",
                mode="flag",
                auth_credentials={"encoded_credentials": "fake_creds"},
            )

        self.assertIn("Unexpected error: Test error", result["errors"])
