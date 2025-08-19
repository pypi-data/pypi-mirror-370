"""Simple test runner for VerificationRangesValidator using built-in unittest.
This script runs VerificationRangesValidator tests without requiring external dependencies.
"""

import sys
import unittest
from unittest.mock import Mock, patch
import os

# Add the project root to the path so we can import urarovite modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from urarovite.validators.format_validation import VerificationRangesValidator
    from urarovite.validators.sheet_name_quoting import (
        run as validate_sheet_name_quoting,
    )
except ImportError as e:
    print(f"❌ Failed to import modules: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)


class TestVerificationRangesValidator(unittest.TestCase):
    """Test suite for VerificationRangesValidator using unittest."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.validator = VerificationRangesValidator()
        self.test_spreadsheet_url = (
            "https://docs.google.com/spreadsheets/d/test_id/edit"
        )
        self.test_auth_credentials = {
            "encoded_creds": "fake_base64_encoded_service_account"
        }

    def test_validator_initialization(self):
        """Test that the validator is properly initialized."""
        self.assertEqual(self.validator.id, "invalid_verification_ranges")
        self.assertEqual(self.validator.name, "Validate Verification Ranges")
        self.assertIn("A1 notation", self.validator.description)

    def test_validate_ranges_with_sheet_name_quoting(self):
        """Test that _validate_ranges correctly uses sheet name quoting validator."""
        # Valid cases
        valid_cases = [
            "'March 2025'!A2:A91@@'Sheet1'!B1",
            "'Tab'!A1",
            "'A'!A1@@'B'!B2:B5",
        ]

        for case in valid_cases:
            with self.subTest(case=case):
                result = self.validator._validate_ranges(case)
                self.assertTrue(result["ok"], f"Should be valid: {case}")
                self.assertIn("failing_segments", result)

        # Invalid cases
        invalid_cases = [
            "March 2025'!A2:A91@@'Sheet1'!B1",  # Missing leading quote
            "'Tab'!A1@@Sheet2!B2",  # Missing quotes on second segment
            "Sheet!A1",  # Missing quotes
            "'A'!A1@@B!B2:B5",  # Mixed quoted/unquoted
        ]

        for case in invalid_cases:
            with self.subTest(case=case):
                result = self.validator._validate_ranges(case)
                self.assertFalse(result["ok"], f"Should be invalid: {case}")
                self.assertGreater(len(result["failing_segments"]), 0)

    def test_fix_ranges_basic(self):
        """Test basic range fixing functionality."""
        test_cases = [
            # Input, Expected Output
            ("Sheet1!A1", "'Sheet1'!A1"),
            ("March 2025!A2:A91", "'March 2025'!A2:A91"),
            ("Sheet With Spaces!B1:B10", "'Sheet With Spaces'!B1:B10"),
            ("Tab1!A1@@Tab2!B2", "'Tab1'!A1@@'Tab2'!B2"),
            ("'Already Quoted'!A1", "'Already Quoted'!A1"),
        ]

        for input_range, expected in test_cases:
            with self.subTest(input_range=input_range):
                result = self.validator._fix_ranges(input_range)
                self.assertEqual(result, expected)

    def test_fix_ranges_malformed_quotes(self):
        """Test fixing ranges with malformed quotes."""
        test_cases = [
            # Input, Expected Output
            ("March 2025'!A2:A91", "'March 2025'!A2:A91"),  # Missing leading quote
            ("'March 2025!A2:A91", "'March 2025'!A2:A91"),  # Missing trailing quote
            ("Sheet1@@Sheet2!B2", "'Sheet1'@@'Sheet2'!B2"),  # Whole sheet + range
        ]

        for input_range, expected in test_cases:
            with self.subTest(input_range=input_range):
                result = self.validator._fix_ranges(input_range)
                self.assertEqual(result, expected)

    def test_fix_segment_individual(self):
        """Test fixing individual segments."""
        test_cases = [
            # Input, Expected Output
            ("Sheet1!A1", "'Sheet1'!A1"),
            ("'Sheet1'!A1", "'Sheet1'!A1"),  # Already correct
            ("March 2025'!A2:A91", "'March 2025'!A2:A91"),  # Fix missing quote
            ("'March 2025!A2:A91", "'March 2025'!A2:A91"),  # Fix missing quote
            ("Sheet With Spaces!B1", "'Sheet With Spaces'!B1"),
            ("OnlySheet", "'OnlySheet'"),  # Whole sheet reference
        ]

        for input_segment, expected in test_cases:
            with self.subTest(input_segment=input_segment):
                result = self.validator._fix_segment(input_segment)
                self.assertEqual(result, expected)

    def test_needs_quoting(self):
        """Test the _needs_quoting method."""
        # Should need quoting (non-alphanumeric or underscore)
        needs_quoting = [
            "Sheet With Spaces",
            "Sheet-1",
            "Sheet.2",
            "Sheet+Plus",
            "March 2025",
            "Tab@Special",
        ]

        for name in needs_quoting:
            with self.subTest(name=name):
                self.assertTrue(self.validator._needs_quoting(name))

        # Should not need quoting (but will still be quoted for consistency)
        no_special_chars = [
            "Sheet1",
            "Tab_1",
            "UPPERCASE",
            "lowercase",
            "Mixed_Case_123",
        ]

        for name in no_special_chars:
            with self.subTest(name=name):
                self.assertFalse(self.validator._needs_quoting(name))

    def test_looks_like_verification_range(self):
        """Test the _looks_like_verification_range method."""
        # Should look like verification ranges
        positive_cases = [
            "'Sheet1'!A1",
            "Sheet1!A1:B10",
            "'Tab1'!A1@@'Tab2'!B2",
            "Sheet!A1:A100@@Other!C1:C50",
            "A1:B10",  # Simple range
            "'March 2025'!A2:A91",
        ]

        for case in positive_cases:
            with self.subTest(case=case):
                self.assertTrue(self.validator._looks_like_verification_range(case))

        # Should not look like verification ranges
        negative_cases = [
            "",
            "Some random text",
            "123456",
            "email@example.com",
            "http://example.com",
            "Just text without ranges",
        ]

        for case in negative_cases:
            with self.subTest(case=case):
                self.assertFalse(self.validator._looks_like_verification_range(case))

    def test_validate_empty_sheet(self):
        """Test validation when spreadsheet is empty."""
        with patch.object(self.validator, "_get_all_sheet_data") as mock_get_data:
            with patch.object(
                self.validator, "_get_spreadsheet"
            ) as mock_get_spreadsheet:
                mock_get_data.return_value = ([], "Sheet1")
                mock_spreadsheet = Mock()
                mock_get_spreadsheet.return_value = mock_spreadsheet

                result = self.validator.validate(
                    spreadsheet_source=self.test_spreadsheet_url,
                    mode="flag",
                    auth_credentials=self.test_auth_credentials,
                )

                self.assertEqual(result["fixes_applied"], 0)
                self.assertEqual(result["flags_found"], 0)
                self.assertEqual(len(result["errors"]), 1)
                self.assertIn("Sheet is empty", result["errors"][0])

    def test_validate_no_flags_found(self):
        """Test validation when no flags are found."""
        # Mock data with valid verification ranges
        mock_data = [
            ["'Sheet1'!A1:A10", "'Sheet2'!B1:B5"],
            ["'March 2025'!A2:A91@@'Sheet1'!B1", "'Tab'!C1:C20"],
        ]

        with patch.object(self.validator, "_get_all_sheet_data") as mock_get_data:
            with patch.object(
                self.validator, "_get_spreadsheet"
            ) as mock_get_spreadsheet:
                mock_get_data.return_value = (mock_data, "Sheet1")
                mock_spreadsheet = Mock()
                mock_get_spreadsheet.return_value = mock_spreadsheet

                result = self.validator.validate(
                    spreadsheet_source=self.test_spreadsheet_url,
                    mode="flag",
                    auth_credentials=self.test_auth_credentials,
                    verification_ranges_columns=[1, 2],
                )

                self.assertEqual(result["fixes_applied"], 0)
                self.assertEqual(result["flags_found"], 0)
                self.assertEqual(result["errors"], [])
                self.assertEqual(result["details"], {})

    def test_validate_flag_mode_with_flags(self):
        """Test validation in flag mode with flags found."""
        # Mock data with invalid verification ranges
        mock_data = [
            ["Sheet1!A1:A10", "Sheet2!B1:B5"],  # Missing quotes
            ["March 2025'!A2:A91@@'Sheet1'!B1", "Tab!C1:C20"],  # Mixed flags
        ]

        with patch.object(self.validator, "_get_all_sheet_data") as mock_get_data:
            with patch.object(
                self.validator, "_get_spreadsheet"
            ) as mock_get_spreadsheet:
                mock_get_data.return_value = (mock_data, "Sheet1")
                mock_spreadsheet = Mock()
                mock_get_spreadsheet.return_value = mock_spreadsheet

                result = self.validator.validate(
                    spreadsheet_source=self.test_spreadsheet_url,
                    mode="flag",
                    auth_credentials=self.test_auth_credentials,
                    verification_ranges_columns=[1, 2],
                )

                self.assertEqual(result["fixes_applied"], 0)
                self.assertGreater(result["flags_found"], 0)
                self.assertEqual(result["errors"], [])
                self.assertIn("flags", result["details"])
                self.assertGreater(len(result["details"]["flags"]), 0)

    def test_validate_fix_mode_with_flags(self):
        """Test validation in fix mode with fixable flags."""
        # Mock data with fixable verification ranges
        mock_data = [
            ["Sheet1!A1:A10", "Sheet2!B1:B5"],  # Missing quotes - fixable
            [
                "'March 2025'!A2:A91@@Sheet3!B1",
                "Tab!C1:C20",
            ],  # Partially quoted - fixable
        ]

        with patch.object(self.validator, "_get_all_sheet_data") as mock_get_data:
            with patch.object(self.validator, "_update_sheet_data") as mock_update_data:
                with patch.object(
                    self.validator, "_get_spreadsheet"
                ) as mock_get_spreadsheet:
                    mock_get_data.return_value = (mock_data, "Sheet1")
                    mock_spreadsheet = Mock()
                    mock_get_spreadsheet.return_value = mock_spreadsheet

                    result = self.validator.validate(
                        spreadsheet_source=self.test_spreadsheet_url,
                        mode="fix",
                        auth_credentials=self.test_auth_credentials,
                        verification_ranges_columns=[1, 2],
                    )

                    self.assertGreater(result["fixes_applied"], 0)
                    self.assertEqual(result["errors"], [])
                    self.assertIn("fixes", result["details"])

                    # Verify that _update_sheet_data was called
                    mock_update_data.assert_called_once()
                    mock_spreadsheet.save.assert_called_once()

    def test_complex_range_scenarios(self):
        """Test complex real-world range scenarios."""
        complex_cases = [
            # Input, Expected after fix
            (
                "'March 2025'!A2:A91@@Summary!B1:B10",
                "'March 2025'!A2:A91@@'Summary'!B1:B10",
            ),
            (
                "Data Entry!A1@@'Q1 Results'!C1:C50@@Final!Z1",
                "'Data Entry'!A1@@'Q1 Results'!C1:C50@@'Final'!Z1",
            ),
            (
                "Sheet1@@Sheet2!A1:B10@@'Sheet 3'!C1",
                "'Sheet1'@@'Sheet2'!A1:B10@@'Sheet 3'!C1",
            ),
            ("'Already Good'!A1@@AlsoGood!B2", "'Already Good'!A1@@'AlsoGood'!B2"),
        ]

        for input_range, expected in complex_cases:
            with self.subTest(input_range=input_range):
                result = self.validator._fix_ranges(input_range)
                self.assertEqual(result, expected)

                # Verify the fixed version passes validation
                validation_result = self.validator._validate_ranges(result)
                self.assertTrue(
                    validation_result["ok"], f"Fixed range should be valid: {result}"
                )

    def test_curly_quotes_conversion(self):
        """Test conversion of curly quotes to straight quotes."""
        # Use Unicode escape sequences to avoid syntax flags
        left_double = "\u201c"  # "
        right_double = "\u201d"  # "
        left_single = "\u2018"  # '
        right_single = "\u2019"  # '

        curly_quote_cases = [
            # Left and right double curly quotes
            (f"{left_double}March 2025{right_double}!A1:B10", "'March 2025'!A1:B10"),
            (f"{left_double}Sheet Name{right_double}!C1", "'Sheet Name'!C1"),
            # Left and right single curly quotes
            (f"{left_single}March 2025{right_single}!A1:B10", "'March 2025'!A1:B10"),
            (f"{left_single}Sheet Name{right_single}!C1", "'Sheet Name'!C1"),
            # Mixed curly quotes
            (
                f"{left_double}Sheet1{left_single}!A1@@{left_single}Sheet2{right_double}!B2",
                "'Sheet1'!A1@@'Sheet2'!B2",
            ),
            (
                f"{left_single}Left{right_single}!A1@@{left_double}Right{right_double}!B2",
                "'Left'!A1@@'Right'!B2",
            ),
            # Complex ranges with curly quotes
            (
                f"{left_double}March 2025{right_double}!A2:A91@@{left_double}Summary{right_double}!B1:B10",
                "'March 2025'!A2:A91@@'Summary'!B1:B10",
            ),
            (
                f"{left_single}Q1 Data{right_single}!A1@@{left_double}Q2 Results{right_double}!C1:C50",
                "'Q1 Data'!A1@@'Q2 Results'!C1:C50",
            ),
            # Whole sheet references with curly quotes
            (f"{left_double}Sheet With Spaces{right_double}", "'Sheet With Spaces'"),
            (f"{left_single}Single Curly{right_single}", "'Single Curly'"),
            # Mixed with regular quotes (should normalize all to straight)
            (
                f"'Normal'!A1@@{left_double}Curly{right_double}!B2@@'Another'!C3",
                "'Normal'!A1@@'Curly'!B2@@'Another'!C3",
            ),
        ]

        for input_range, expected in curly_quote_cases:
            with self.subTest(input_range=input_range):
                result = self.validator._fix_ranges(input_range)
                self.assertEqual(
                    result,
                    expected,
                    f"Failed to convert curly quotes in: {input_range}",
                )

    def test_convert_curly_quotes_method(self):
        """Test the _convert_curly_quotes method directly."""
        # Use Unicode escape sequences to avoid syntax flags
        left_double = "\u201c"  # "
        right_double = "\u201d"  # "
        left_single = "\u2018"  # '
        right_single = "\u2019"  # '

        test_cases = [
            # Empty/None cases
            ("", ""),
            (None, None),
            # Double curly quotes
            (f"{left_double}Hello{right_double}", "'Hello'"),
            (f"{left_double}World{right_double}", "'World'"),
            (
                f"{left_double}Mixed{right_double} and {left_double}quotes{right_double}",
                "'Mixed' and 'quotes'",
            ),
            # Single curly quotes
            (f"{left_single}Left{right_single}", "'Left'"),
            (f"{left_single}Right{right_single}", "'Right'"),
            (
                f"{left_single}Both{right_single} and {left_single}sides{right_single}",
                "'Both' and 'sides'",
            ),
            # Mixed curly and straight quotes
            (f"'Mixed{right_double} and {left_double}types'", "'Mixed' and 'types'"),
            (
                f"{left_double}Double' and 'single{right_double}",
                "'Double' and 'single'",
            ),
            # Complex sheet names with curly quotes
            (
                f"{left_double}March 2025 Data{right_double}!A1:B10",
                "'March 2025 Data'!A1:B10",
            ),
            (f"{left_single}Q1 Results{right_single}!C1:C50", "'Q1 Results'!C1:C50"),
            # Text without quotes (should remain unchanged)
            ("Sheet1!A1", "Sheet1!A1"),
            ("Normal text", "Normal text"),
        ]

        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = self.validator._convert_curly_quotes(input_text)
                self.assertEqual(
                    result, expected, f"Failed to convert: {repr(input_text)}"
                )

    def test_curly_quotes_in_complex_scenarios(self):
        """Test curly quotes in complex real-world scenarios."""
        # Use Unicode escape sequences to avoid syntax flags
        left_double = "\u201c"  # "
        right_double = "\u201d"  # "
        left_single = "\u2018"  # '
        right_single = "\u2019"  # '

        complex_cases = [
            # Multiple segments with different curly quote types
            (
                f"{left_double}Data Entry{right_double}!A1@@{left_single}Summary{right_single}!B2@@{left_double}Final Report{right_double}!C3",
                "'Data Entry'!A1@@'Summary'!B2@@'Final Report'!C3",
            ),
            # Curly quotes with special characters in sheet names
            (
                f"{left_double}Sheet & Data{right_double}!A1:B10@@{left_single}Results (Q1){right_single}!C1",
                "'Sheet & Data'!A1:B10@@'Results (Q1)'!C1",
            ),
            # Mixed curly quotes with ranges
            (
                f"{left_single}March 2025{right_single}!A2:A91@@{left_double}April 2025{right_double}!B1:B50",
                "'March 2025'!A2:A91@@'April 2025'!B1:B50",
            ),
            # Curly quotes in whole sheet references
            (
                f"{left_double}Tab 1{right_double}@@{left_single}Tab 2{right_single}@@{left_double}Tab 3{right_double}",
                "'Tab 1'@@'Tab 2'@@'Tab 3'",
            ),
        ]

        for input_range, expected in complex_cases:
            with self.subTest(input_range=input_range):
                result = self.validator._fix_ranges(input_range)
                self.assertEqual(result, expected)

                # Verify the fixed version passes validation
                validation_result = self.validator._validate_ranges(result)
                self.assertTrue(
                    validation_result["ok"], f"Fixed range should be valid: {result}"
                )

    def test_edge_cases(self):
        """Test various edge cases."""
        edge_cases = [
            ("", ""),  # Empty string
            ("   ", ""),  # Whitespace only
            ("@@@@", ""),  # Only separators
            ("A1", "'A1'"),  # Simple cell reference
            ("Sheet1!A1@@@@Sheet2!B2", "'Sheet1'!A1@@'Sheet2'!B2"),  # Extra separators
        ]

        for input_range, expected in edge_cases:
            with self.subTest(input_range=input_range):
                if input_range.strip():
                    result = self.validator._fix_ranges(input_range)
                    self.assertEqual(result, expected)


def run_tests():
    """Run all the tests and provide a summary."""
    print("Running VerificationRangesValidator Tests")
    print("=" * 50)

    # Create a test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestVerificationRangesValidator)

    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print(f"✅ All {result.testsRun} tests passed!")
    else:
        print(
            f"❌ {len(result.failures)} failures, {len(result.errors)} errors out of {result.testsRun} tests"
        )

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
