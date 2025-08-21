"""Tests for DifferentWithinRangesValidator.

This module contains comprehensive tests for the validator that ensures
input and output spreadsheets differ within all specified verification ranges.
"""

import sys
import unittest
from unittest.mock import Mock, patch
import os

# Add the project root to the path so we can import urarovite modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import pandas as pd
    from urarovite.validators.different_within_ranges import (
        DifferentWithinRangesValidator,
    )
    from urarovite.core.exceptions import ValidationError
except ImportError as e:
    print(f"❌ Failed to import modules: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)


class TestDifferentWithinRangesValidator(unittest.TestCase):
    """Test suite for DifferentWithinRangesValidator."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.validator = DifferentWithinRangesValidator()
        self.test_spreadsheet_url = (
            "https://docs.google.com/spreadsheets/d/test_id/edit"
        )
        self.test_auth_credentials = {"auth_secret": "fake_auth_secret"}

    def test_validator_initialization(self):
        """Test that the validator is properly initialized."""
        self.assertEqual(self.validator.id, "different_within_ranges")
        self.assertEqual(self.validator.name, "Different Within Ranges Validator")
        self.assertIn("different within all specified", self.validator.description)

    def test_col_to_n(self):
        """Test column letter to number conversion."""
        self.assertEqual(self.validator._col_to_n("A"), 1)
        self.assertEqual(self.validator._col_to_n("B"), 2)
        self.assertEqual(self.validator._col_to_n("Z"), 26)
        self.assertEqual(self.validator._col_to_n("AA"), 27)
        self.assertEqual(self.validator._col_to_n("AB"), 28)

    def test_a1_dims(self):
        """Test A1 range dimension calculation."""
        # Single cell
        self.assertEqual(self.validator._a1_dims("A1"), (1, 1))
        self.assertEqual(self.validator._a1_dims("'Tab'!A1"), (1, 1))

        # Ranges
        self.assertEqual(self.validator._a1_dims("A1:B2"), (2, 2))
        self.assertEqual(self.validator._a1_dims("'Tab'!A1:C3"), (3, 3))
        self.assertEqual(self.validator._a1_dims("B2:D5"), (4, 3))

    def test_extract_tab(self):
        """Test tab extraction from A1 ranges."""
        self.assertEqual(self.validator._extract_tab("A1"), "")
        self.assertEqual(self.validator._extract_tab("A1:B2"), "")
        self.assertEqual(self.validator._extract_tab("Tab!A1"), "Tab")
        self.assertEqual(self.validator._extract_tab("'My Tab'!A1:B2"), "My Tab")

    def test_range_part(self):
        """Test range part extraction."""
        self.assertEqual(self.validator._range_part("A1"), "A1")
        self.assertEqual(self.validator._range_part("A1:B2"), "A1:B2")
        self.assertEqual(self.validator._range_part("Tab!A1"), "A1")
        self.assertEqual(self.validator._range_part("'My Tab'!A1:B2"), "A1:B2")

    def test_pad(self):
        """Test matrix padding functionality."""
        # Empty matrix
        result = self.validator._pad(None, 2, 2)
        expected = [["", ""], ["", ""]]
        self.assertEqual(result, expected)

        # Partial matrix
        input_mat = [["A"]]
        result = self.validator._pad(input_mat, 2, 2)
        expected = [["A", ""], ["", ""]]
        self.assertEqual(result, expected)

        # Complete matrix
        input_mat = [["A", "B"], ["C", "D"]]
        result = self.validator._pad(input_mat, 2, 2)
        self.assertEqual(result, input_mat)

    def test_validate_missing_row(self):
        """Test validation with missing row parameter."""
        result = self.validator.validate(
            spreadsheet_source=self.test_spreadsheet_url,
            mode="flag",
            auth_credentials=self.test_auth_credentials,
        )

        # Should return empty ValidationResult
        self.assertEqual(result["flags_found"], 0)
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["automated_log"], "No flags found")

    def test_validate_missing_urls(self):
        """Test validation with missing or invalid URLs."""
        row = pd.Series(
            {
                "verification_field_ranges": "A1:B2",
                "input_sheet_url": "invalid_url",
                "example_output_sheet_url": "also_invalid",
            }
        )

        result = self.validator.validate(
            spreadsheet_source=self.test_spreadsheet_url,
            mode="flag",
            auth_credentials=self.test_auth_credentials,
            row=row,
        )

        # Should have errors due to missing sheet IDs
        self.assertEqual(result["flags_found"], 0)
        self.assertEqual(len(result["errors"]), 1)
        self.assertIn("Missing input/output spreadsheet IDs", result["errors"][0])
        self.assertEqual(result["details"]["total_segments"], 1)
        self.assertEqual(result["details"]["total_diff_cells"], 0)

    @patch("urarovite.validators.different_within_ranges.extract_sheet_id")
    @patch(
        "urarovite.validators.different_within_ranges.create_sheets_service_from_encoded_creds"
    )
    def test_validate_successful_all_different(self, mock_create_service, mock_extract):
        """Test successful validation when all ranges differ."""
        # Mock sheet ID extraction
        mock_extract.side_effect = (
            lambda url: "input_id" if "input" in url else "output_id"
        )

        # Mock service with batch get
        mock_service = Mock()
        # First call (input sheet) - returns 2 ranges for 2 segments
        input_response = {
            "valueRanges": [
                {"values": [["A", "B"], ["C", "D"]]},  # Input segment 1
                {"values": [["E", "F"], ["G", "H"]]},  # Input segment 2
            ]
        }
        # Second call (output sheet) - returns 2 ranges for 2 segments
        output_response = {
            "valueRanges": [
                {"values": [["X", "Y"], ["Z", "W"]]},  # Output segment 1 (different)
                {"values": [["I", "J"], ["K", "L"]]},  # Output segment 2 (different)
            ]
        }
        mock_service.spreadsheets().values().batchGet().execute.side_effect = [
            input_response,
            output_response,
        ]
        mock_create_service.return_value = mock_service

        row = pd.Series(
            {
                "verification_field_ranges": "A1:B2@@C1:D2",
                "input_sheet_url": "https://docs.google.com/spreadsheets/d/input_id/edit",
                "example_output_sheet_url": "https://docs.google.com/spreadsheets/d/output_id/edit",
            }
        )

        result = self.validator.validate(
            spreadsheet_source=self.test_spreadsheet_url,
            mode="flag",
            auth_credentials=self.test_auth_credentials,
            row=row,
        )

        # All ranges differ, so no flags
        self.assertEqual(result["flags_found"], 0)
        self.assertEqual(result["details"]["total_segments"], 2)
        self.assertEqual(
            result["details"]["total_diff_cells"], 8
        )  # 4 cells per segment, all different
        self.assertEqual(result["errors"], [])

        # Check segment details
        self.assertEqual(len(result["details"]["segments"]), 2)
        self.assertFalse(result["details"]["segments"][0]["identical"])
        self.assertFalse(result["details"]["segments"][1]["identical"])
        self.assertEqual(
            result["details"]["segments"][0]["diff_count"], 4
        )  # 2x2 cells, all different
        self.assertEqual(
            result["details"]["segments"][1]["diff_count"], 4
        )  # 2x2 cells, all different

    @patch("urarovite.validators.different_within_ranges.extract_sheet_id")
    @patch(
        "urarovite.validators.different_within_ranges.create_sheets_service_from_encoded_creds"
    )
    def test_validate_partial_identical(self, mock_create_service, mock_extract):
        """Test validation when some ranges are identical (should fail)."""
        # Mock sheet ID extraction
        mock_extract.side_effect = (
            lambda url: "input_id" if "input" in url else "output_id"
        )

        # Mock service with batch get - first range identical, second different
        mock_service = Mock()
        # First call (input sheet) - returns 2 ranges for 2 segments
        input_response = {
            "valueRanges": [
                {"values": [["A"]]},  # Input segment 1
                {"values": [["X"]]},  # Input segment 2
            ]
        }
        # Second call (output sheet) - returns 2 ranges for 2 segments
        output_response = {
            "valueRanges": [
                {"values": [["A"]]},  # Output segment 1 (identical to input)
                {"values": [["Y"]]},  # Output segment 2 (different from input)
            ]
        }
        mock_service.spreadsheets().values().batchGet().execute.side_effect = [
            input_response,
            output_response,
        ]
        mock_create_service.return_value = mock_service

        row = pd.Series(
            {
                "verification_field_ranges": "A1@@B1",
                "input_sheet_url": "https://docs.google.com/spreadsheets/d/input_id/edit",
                "example_output_sheet_url": "https://docs.google.com/spreadsheets/d/output_id/edit",
            }
        )

        result = self.validator.validate(
            spreadsheet_source=self.test_spreadsheet_url,
            mode="flag",
            auth_credentials=self.test_auth_credentials,
            row=row,
        )

        # Should have flags because first range is identical
        self.assertEqual(result["flags_found"], 1)  # 1 identical segment
        self.assertEqual(result["details"]["total_segments"], 2)
        self.assertEqual(result["details"]["total_diff_cells"], 1)
        self.assertEqual(result["errors"], [])

        # Check segment details
        self.assertEqual(len(result["details"]["segments"]), 2)
        self.assertTrue(
            result["details"]["segments"][0]["identical"]
        )  # First range is identical
        self.assertFalse(
            result["details"]["segments"][1]["identical"]
        )  # Second range is different
        self.assertEqual(result["details"]["segments"][0]["diff_count"], 0)
        self.assertEqual(result["details"]["segments"][1]["diff_count"], 1)

    @patch("urarovite.validators.different_within_ranges.extract_sheet_id")
    @patch(
        "urarovite.validators.different_within_ranges.create_sheets_service_from_encoded_creds"
    )
    def test_validate_single_range_different(self, mock_create_service, mock_extract):
        """Test validation with single range that differs."""
        # Mock sheet ID extraction
        mock_extract.side_effect = (
            lambda url: "input_id" if "input" in url else "output_id"
        )

        # Mock service with single different range
        mock_service = Mock()
        # First call (input sheet) - returns 1 range for 1 segment
        input_response = {
            "valueRanges": [
                {"values": [["Input"]]}  # Input segment 1
            ]
        }
        # Second call (output sheet) - returns 1 range for 1 segment
        output_response = {
            "valueRanges": [
                {"values": [["Output"]]}  # Output segment 1 (different from input)
            ]
        }
        mock_service.spreadsheets().values().batchGet().execute.side_effect = [
            input_response,
            output_response,
        ]
        mock_create_service.return_value = mock_service

        row = pd.Series(
            {
                "verification_field_ranges": "A1",
                "input_sheet_url": "https://docs.google.com/spreadsheets/d/input_id/edit",
                "example_output_sheet_url": "https://docs.google.com/spreadsheets/d/output_id/edit",
            }
        )

        result = self.validator.validate(
            spreadsheet_source=self.test_spreadsheet_url,
            mode="flag",
            auth_credentials=self.test_auth_credentials,
            row=row,
        )

        # Single range differs, so no flags
        self.assertEqual(result["flags_found"], 0)
        self.assertEqual(result["details"]["total_segments"], 1)
        self.assertEqual(result["details"]["total_diff_cells"], 1)

    @patch("urarovite.validators.different_within_ranges.extract_sheet_id")
    @patch(
        "urarovite.validators.different_within_ranges.create_sheets_service_from_encoded_creds"
    )
    def test_validate_api_error(self, mock_create_service, mock_extract):
        """Test validation when API call fails."""
        # Mock sheet ID extraction
        mock_extract.side_effect = (
            lambda url: "input_id" if "input" in url else "output_id"
        )

        # Mock service that raises an exception
        mock_service = Mock()
        mock_service.spreadsheets().values().batchGet().execute.side_effect = Exception(
            "API Error"
        )
        mock_create_service.return_value = mock_service

        row = pd.Series(
            {
                "verification_field_ranges": "A1",
                "input_sheet_url": "https://docs.google.com/spreadsheets/d/input_id/edit",
                "example_output_sheet_url": "https://docs.google.com/spreadsheets/d/output_id/edit",
            }
        )

        # Should raise ValidationError
        with self.assertRaises(ValidationError) as context:
            self.validator.validate(
                spreadsheet_source=self.test_spreadsheet_url,
                mode="flag",
                auth_credentials=self.test_auth_credentials,
                row=row,
            )

        self.assertIn(
            "Failed to validate different within ranges", str(context.exception)
        )
        self.assertIn("API Error", str(context.exception))

    def test_expand_a1_range(self):
        """Test A1 range expansion."""
        # Simple range
        tab, coords = self.validator._expand_a1_range("A1:B2")
        self.assertEqual(tab, "")
        self.assertEqual(coords, (0, 0, 1, 1))  # (r1, c1, r2, c2) zero-based

        # Range with tab
        tab, coords = self.validator._expand_a1_range("'Sheet1'!C3:D4")
        self.assertEqual(tab, "Sheet1")
        self.assertEqual(coords, (2, 2, 3, 3))

        # Single cell
        tab, coords = self.validator._expand_a1_range("A1")
        self.assertEqual(tab, "")
        self.assertEqual(coords, (0, 0, 0, 0))

    def test_a1_to_rc(self):
        """Test A1 to row-column conversion."""
        self.assertEqual(self.validator._a1_to_rc("A1"), (0, 0))
        self.assertEqual(self.validator._a1_to_rc("B2"), (1, 1))
        self.assertEqual(self.validator._a1_to_rc("Z26"), (25, 25))
        self.assertEqual(self.validator._a1_to_rc("AA1"), (0, 26))

    def test_a1_from_rc(self):
        """Test row-column to A1 conversion."""
        self.assertEqual(self.validator._a1_from_rc(0, 0), "A1")
        self.assertEqual(self.validator._a1_from_rc(1, 1), "B2")
        self.assertEqual(self.validator._a1_from_rc(25, 25), "Z26")
        self.assertEqual(self.validator._a1_from_rc(0, 26), "AA1")

    @patch("urarovite.validators.different_within_ranges.extract_sheet_id")
    @patch(
        "urarovite.validators.different_within_ranges.create_sheets_service_from_encoded_creds"
    )
    def test_validate_comprehensive_scenario(self, mock_create_service, mock_extract):
        """Test a comprehensive scenario with multiple ranges and mixed results."""
        mock_extract.side_effect = (
            lambda url: "input_id" if "input" in url else "output_id"
        )

        mock_service = Mock()
        # First call (input sheet) - returns 2 ranges for 2 segments
        input_response = {
            "valueRanges": [
                {"values": [["A1"], ["A2"]]},  # Input segment 1 (Sheet1!A1:A2)
                {"values": [["X"]]},  # Input segment 2 (Sheet2!B1)
            ]
        }
        # Second call (output sheet) - returns 2 ranges for 2 segments
        output_response = {
            "valueRanges": [
                {"values": [["B1"], ["B2"]]},  # Output segment 1 (different from input)
                {"values": [["Y"]]},  # Output segment 2 (different from input)
            ]
        }
        mock_service.spreadsheets().values().batchGet().execute.side_effect = [
            input_response,
            output_response,
        ]
        mock_create_service.return_value = mock_service

        row = pd.Series(
            {
                "verification_field_ranges": "'Sheet1'!A1:A2@@'Sheet2'!B1",
                "input_sheet_url": "https://docs.google.com/spreadsheets/d/input_id/edit",
                "example_output_sheet_url": "https://docs.google.com/spreadsheets/d/output_id/edit",
            }
        )

        result = self.validator.validate(
            spreadsheet_source=self.test_spreadsheet_url,
            mode="flag",
            auth_credentials=self.test_auth_credentials,
            row=row,
        )

        # All ranges are different, so no flags
        self.assertEqual(result["flags_found"], 0)
        self.assertEqual(
            result["details"]["total_diff_cells"], 3
        )  # Segment 1: 2 cells, Segment 2: 1 cell

        segment = result["details"]["segments"][0]
        self.assertEqual(segment["segment"], "'Sheet1'!A1:A2")
        self.assertEqual(segment["tab"], "Sheet1")
        self.assertEqual(segment["range_part"], "A1:A2")
        self.assertFalse(segment["identical"])
        self.assertEqual(segment["diff_count"], 2)  # A1:A2 = 2 cells, all different

    @patch("urarovite.validators.different_within_ranges.extract_sheet_id")
    @patch(
        "urarovite.validators.different_within_ranges.create_sheets_service_from_encoded_creds"
    )
    def test_validate_custom_separator(self, mock_create_service, mock_extract):
        """Test validation with custom separator (comma instead of @@)."""
        mock_extract.side_effect = (
            lambda url: "input_id" if "input" in url else "output_id"
        )

        mock_service = Mock()
        # Mock responses for comma-separated ranges
        input_response = {
            "valueRanges": [
                {"values": [["A1"]]},  # Input segment 1
                {"values": [["B1"]]},  # Input segment 2
            ]
        }
        output_response = {
            "valueRanges": [
                {"values": [["X1"]]},  # Output segment 1 (different)
                {"values": [["Y1"]]},  # Output segment 2 (different)
            ]
        }
        mock_service.spreadsheets().values().batchGet().execute.side_effect = [
            input_response,
            output_response,
        ]
        mock_create_service.return_value = mock_service

        row = pd.Series(
            {
                "verification_field_ranges": "'Sheet1'!A1,'Sheet2'!B1",  # Comma-separated
                "input_sheet_url": "https://docs.google.com/spreadsheets/d/input_id/edit",
                "example_output_sheet_url": "https://docs.google.com/spreadsheets/d/output_id/edit",
            }
        )

        result = self.validator.validate(
            spreadsheet_source=self.test_spreadsheet_url,
            mode="flag",
            auth_credentials=self.test_auth_credentials,
            row=row,
            separator=",",  # Use comma separator
        )

        # Should parse 2 segments with comma separator
        self.assertEqual(result["details"]["total_segments"], 2)
        # All ranges are different, so no flags
        self.assertEqual(result["flags_found"], 0)
        self.assertEqual(
            result["details"]["total_diff_cells"], 2
        )  # 2 segments, 1 cell each


class TestBackwardCompatibility(unittest.TestCase):
    """Test backward compatibility with the original function interface."""

    @patch(
        "urarovite.validators.different_within_ranges.DifferentWithinRangesValidator.validate"
    )
    def test_run_function(self, mock_validate):
        """Test the backward compatibility run function."""
        from urarovite.validators.different_within_ranges import run

        # Mock the validator's validate method
        mock_validate.return_value = {"flags_found": 0, "details": {}}

        row = pd.Series(
            {
                "verification_field_ranges": "A1:B2",
                "input_sheet_url": "https://docs.google.com/spreadsheets/d/input_id/edit",
                "example_output_sheet_url": "https://docs.google.com/spreadsheets/d/output_id/edit",
            }
        )

        run(row)

        # Verify the validate method was called with correct parameters
        mock_validate.assert_called_once()
        args, kwargs = mock_validate.call_args

        # Check that the call was made with correct parameters
        # The run function calls validate with keyword arguments
        self.assertEqual(kwargs["spreadsheet_source"], "")  # spreadsheet_source
        self.assertEqual(kwargs["mode"], "flag")  # mode
        self.assertIsNone(kwargs["auth_credentials"])  # auth_credentials
        self.assertEqual(kwargs["row"].equals(row), True)
        self.assertEqual(kwargs["field"], "verification_field_ranges")
        self.assertEqual(kwargs["input_col"], "input_sheet_url")
        self.assertEqual(kwargs["output_col"], "example_output_sheet_url")
        self.assertEqual(kwargs["max_report_per_segment"], 100)


if __name__ == "__main__":
    unittest.main()
