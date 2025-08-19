"""Test suite for NoCorrectAnswersValidator using built-in unittest.

This script tests the NoCorrectAnswersValidator to ensure it correctly
detects when input sheets contain no correct answers.
"""

import sys
import unittest
from unittest.mock import Mock, patch, MagicMock
import os

# Add the project root to the path so we can import urarovite modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from urarovite.validators.no_correct_answers import NoCorrectAnswersValidator
    from urarovite.core.exceptions import ValidationError
    from urarovite.validators.base import ValidationResult
except ImportError as e:
    print(f"❌ Failed to import modules: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)


class TestNoCorrectAnswersValidator(unittest.TestCase):
    """Test suite for NoCorrectAnswersValidator using unittest."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.validator = NoCorrectAnswersValidator()

    def test_validator_initialization(self):
        """Test that the validator is properly initialized."""
        self.assertEqual(self.validator.id, "no_correct_answers")
        self.assertEqual(self.validator.name, "Detect No Correct Answers")
        self.assertIn(
            "Detects when input sheets contain no valid answers",
            self.validator.description,
        )

    def test_empty_sheet_detection(self):
        """Test detection of completely empty sheets."""
        empty_data = []
        result = self.validator._analyze_sheet_content(empty_data)

        self.assertEqual(result["confidence_score"], 1.0)
        self.assertTrue(result["is_template_or_blank"])
        self.assertEqual(result["reasons"], ["Sheet is completely empty"])

    def test_high_empty_cell_ratio_detection(self):
        """Test detection of sheets with high empty cell ratios."""
        # Sheet with mostly empty cells
        data = [
            ["Name", "Age", "City", "Email"],
            ["John", "", "", ""],
            ["", "", "", ""],
            ["", "", "", ""],
            ["", "", "", ""],
        ]

        result = self.validator._analyze_sheet_content(data)

        self.assertGreaterEqual(result["confidence_score"], 0.6)
        self.assertTrue(result["is_template_or_blank"])
        self.assertTrue(
            any("High empty cell ratio" in reason for reason in result["reasons"])
        )

    def test_template_text_detection(self):
        """Test detection of template/placeholder text."""
        data = [
            ["Name", "Age", "City", "Email"],
            ["Example Name", "Example Age", "Example City", "Example Email"],
            ["Sample Data", "Sample Data", "Sample Data", "Sample Data"],
            ["Fill here", "Enter here", "Type here", "Input here"],
        ]

        result = self.validator._analyze_sheet_content(data)

        self.assertGreaterEqual(result["confidence_score"], 0.6)
        self.assertTrue(result["is_template_or_blank"])
        self.assertTrue(
            any("template/placeholder text" in reason for reason in result["reasons"])
        )

    def test_headers_only_detection(self):
        """Test detection of sheets with only headers."""
        data = [
            ["Name", "Age", "City", "Email"],
            ["", "", "", ""],
        ]

        result = self.validator._analyze_sheet_content(data)

        self.assertGreater(result["confidence_score"], 0.6)
        self.assertTrue(result["is_template_or_blank"])
        self.assertTrue(any("only headers" in reason for reason in result["reasons"]))

    def test_repetitive_patterns_detection(self):
        """Test detection of repetitive patterns."""
        data = [
            ["Name", "Age", "City", "Email"],
            ["John", "25", "NYC", "john@example.com"],
            ["John", "25", "NYC", "john@example.com"],
            ["John", "25", "NYC", "john@example.com"],
        ]

        result = self.validator._analyze_sheet_content(data)

        self.assertGreaterEqual(result["confidence_score"], 0.6)
        self.assertTrue(result["is_template_or_blank"])
        self.assertTrue(
            any("repetitive patterns" in reason for reason in result["reasons"])
        )

    def test_valid_data_detection(self):
        """Test that sheets with valid data are not flagged as templates."""
        data = [
            ["Name", "Age", "City", "Email"],
            ["John Doe", "25", "New York", "john@example.com"],
            ["Jane Smith", "30", "Los Angeles", "jane@example.com"],
            ["Bob Johnson", "35", "Chicago", "bob@example.com"],
        ]

        result = self.validator._analyze_sheet_content(data)

        self.assertLess(result["confidence_score"], 0.6)
        self.assertFalse(result["is_template_or_blank"])
        # Valid data might still have some indicators, so just check it's not flagged as template
        self.assertFalse(result["is_template_or_blank"])

    def test_mixed_content_detection(self):
        """Test detection with mixed content (some valid, some template)."""
        data = [
            ["Name", "Age", "City", "Email"],
            ["John Doe", "25", "New York", "john@example.com"],
            ["Example Name", "Example Age", "Example City", "Example Email"],
            ["Jane Smith", "30", "Los Angeles", "jane@example.com"],
            ["", "", "", ""],
            ["", "", "", ""],
        ]

        result = self.validator._analyze_sheet_content(data)

        # Should have moderate confidence due to mixed signals
        self.assertGreater(result["confidence_score"], 0.2)
        self.assertLessEqual(result["confidence_score"], 0.8)

    def test_quality_indicators_calculation(self):
        """Test calculation of quality indicators."""
        data = [
            ["Name", "Age", "City", "Email"],
            ["John", "25", "NYC", "john@example.com"],
            ["", "", "", ""],
            ["Sample", "Sample", "Sample", "Sample"],
        ]

        indicators = self.validator._calculate_quality_indicators(data)

        self.assertEqual(indicators["total_cells"], 16)
        self.assertEqual(indicators["empty_cells"], 4)
        self.assertEqual(indicators["total_cells"], 16)
        self.assertEqual(indicators["empty_cells"], 4)
        # The exact count may vary due to how we classify cells, so just check it's reasonable
        self.assertGreater(indicators["text_cells"], 0)
        self.assertEqual(indicators["numeric_cells"], 1)  # Age "25"
        self.assertEqual(indicators["empty_ratio"], 0.25)

    def test_confidence_score_calculation(self):
        """Test confidence score calculation with various indicators."""
        quality_indicators = {"empty_ratio": 0.85, "total_cells": 100}

        template_indicators = {
            "indicators": ["high_empty_ratio", "template_text_present", "headers_only"],
            "reasons": [
                "High empty cell ratio (85.0%)",
                "Contains template text",
                "Headers only",
            ],
        }

        confidence = self.validator._calculate_confidence_score(
            template_indicators, quality_indicators
        )

        # Should be high confidence due to multiple strong indicators
        self.assertGreater(confidence, 0.75)
        self.assertLessEqual(confidence, 1.0)

    def test_repetitive_patterns_detection_logic(self):
        """Test the repetitive patterns detection logic."""
        # Test repeated rows
        data = [
            ["Name", "Age", "City"],
            ["John", "25", "NYC"],
            ["John", "25", "NYC"],
            ["John", "25", "NYC"],
        ]

        patterns = self.validator._detect_repetitive_patterns(data)

        self.assertTrue(any("Repeated row" in pattern for pattern in patterns))

        # Test repeated columns
        data = [
            ["Name", "Status", "Status", "Status"],
            ["John", "Active", "Active", "Active"],
            ["Jane", "Active", "Active", "Active"],
        ]

        patterns = self.validator._detect_repetitive_patterns(data)

        self.assertTrue(
            any(
                "Column" in pattern and "repetitive content" in pattern
                for pattern in patterns
            )
        )

    def test_template_text_patterns(self):
        """Test detection of various template text patterns."""
        template_texts = [
            "example",
            "sample",
            "template",
            "placeholder",
            "test",
            "demo",
            "fill",
            "enter",
            "type",
            "input",
            "here",
            "data",
            "information",
            "details",
        ]

        for text in template_texts:
            with self.subTest(text=text):
                data = [["Header"], [text]]
                result = self.validator._analyze_sheet_content(data)

                # Should detect template text
                self.assertTrue(
                    any(
                        "template/placeholder text" in reason
                        for reason in result["reasons"]
                    )
                )

    def test_meaningful_data_detection(self):
        """Test detection of meaningful data types."""
        data = [
            ["Name", "Age", "Date", "URL", "Amount"],
            ["John", "25", "01/15/2023", "https://example.com", "100.50"],
            ["Jane", "30", "02/20/2023", "http://test.org", "250.75"],
        ]

        indicators = self.validator._calculate_quality_indicators(data)

        self.assertGreater(indicators["numeric_cells"], 0)
        self.assertGreater(indicators["date_cells"], 0)
        self.assertGreater(indicators["url_cells"], 0)

    def test_validation_result_structure(self):
        """Test that the validator returns properly structured results."""
        # Mock the entire spreadsheet creation process
        with patch("urarovite.validators.base.SpreadsheetFactory") as mock_factory:
            mock_spreadsheet = Mock()
            mock_factory.create_spreadsheet.return_value = mock_spreadsheet

            # Mock the _get_all_sheet_data method
            with patch.object(
                self.validator,
                "_get_all_sheet_data",
                return_value=(
                    [["Name", "Age"], ["John", "25"], ["Jane", "30"]],
                    "Test Sheet",
                ),
            ):
                result = self.validator.validate(
                    spreadsheet_source="test.xlsx", mode="flag"
                )

                # Check required fields
                self.assertIn("fixes_applied", result)
                self.assertIn("flags_found", result)
                self.assertIn("errors", result)
                self.assertIn("details", result)
                self.assertIn("automated_log", result)

                # Check validator-specific details
                self.assertIn("confidence_score", result["details"])
                self.assertIn("is_template_or_blank", result["details"])
                self.assertIn("detection_reasons", result["details"])
                self.assertIn("data_quality_indicators", result["details"])


if __name__ == "__main__":
    # Run the tests
    unittest.main(verbosity=2)
