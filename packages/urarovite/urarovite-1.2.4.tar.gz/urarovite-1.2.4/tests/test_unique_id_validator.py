"""Tests for the UniqueIDValidator."""

import unittest
import re
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

from urarovite.validators.unique_id_validator import (
    UniqueIDValidator,
    ID_FIELD_PATTERNS,
)
from urarovite.validators.base import ValidationResult


class TestUniqueIDValidator(unittest.TestCase):
    """Test cases for UniqueIDValidator."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.validator = UniqueIDValidator()
        self.mock_spreadsheet = Mock()
        self.mock_spreadsheet.get_sheet_data.return_value = Mock(
            values=[
                ["ID", "Name", "Reference", "Email"],
                ["001", "John", "REF001", "john@example.com"],
                ["002", "Jane", "REF001", "jane@example.com"],  # Duplicate reference
                ["", "Bob", "REF003", "bob@example.com"],  # Missing ID
                ["004", "Alice", "REF004", "invalid-email"],  # Invalid email format
                ["005", "Eve", "REF005", "eve@example.com"],
            ],
            sheet_name="Sheet1",
        )

    def test_identify_id_columns(self) -> None:
        """Test identification of ID columns from headers."""
        headers = ["ID", "Name", "Reference", "Email", "User_Key", "Code"]

        id_columns = self.validator._identify_id_columns(headers)

        expected_columns = [
            (0, "ID"),  # Basic ID
            (2, "Reference"),  # Reference pattern
            (4, "User_Key"),  # Key pattern
            (5, "Code"),  # Code pattern
        ]

        self.assertEqual(id_columns, expected_columns)

    def test_identify_id_columns_with_custom_patterns(self) -> None:
        """Test identification of ID columns with custom patterns."""
        headers = ["CustomField", "Name", "OtherField"]
        custom_patterns = [r"^custom.*$"]

        id_columns = self.validator._identify_id_columns(headers, custom_patterns)

        expected_columns = [(0, "CustomField")]
        self.assertEqual(id_columns, expected_columns)

    def test_validate_id_column_duplicates(self) -> None:
        """Test detection of duplicate IDs in a column."""
        data = [
            ["ID", "Name"],
            ["001", "John"],
            ["002", "Jane"],
            ["001", "Bob"],  # Duplicate ID
            ["003", "Alice"],
        ]

        results = self.validator._validate_id_column(data, 0, "ID", True)

        self.assertEqual(len(results["duplicates"]), 1)
        duplicate = results["duplicates"][0]
        self.assertEqual(duplicate["value"], "001")
        self.assertEqual(
            duplicate["rows"], [2, 4]
        )  # Row numbers where duplicates occur

    def test_validate_id_column_missing_ids(self) -> None:
        """Test detection of missing/empty IDs."""
        data = [
            ["ID", "Name"],
            ["001", "John"],
            ["", "Jane"],  # Empty ID
            ["002", "Bob"],
            [None, "Alice"],  # None ID
        ]

        results = self.validator._validate_id_column(data, 0, "ID", True)

        self.assertEqual(len(results["missing_ids"]), 2)
        missing_rows = [issue["row"] for issue in results["missing_ids"]]
        self.assertEqual(missing_rows, [3, 5])

    def test_validate_id_column_format_flags(self) -> None:
        """Test detection of format flags in IDs."""
        data = [
            ["ID", "Name"],
            ["001", "John"],
            ["ID with spaces", "Jane"],  # ID with spaces
            ["002", "Bob"],
            ["ID@#$%", "Alice"],  # ID with special characters
        ]

        results = self.validator._validate_id_column(data, 0, "ID", True)

        self.assertEqual(len(results["format_flags"]), 2)
        format_flags = [issue["value"] for issue in results["format_flags"]]
        self.assertIn("ID with spaces", format_flags)
        self.assertIn("ID@#$%", format_flags)

    def test_check_id_format_valid_formats(self) -> None:
        """Test ID format validation with valid formats."""
        valid_formats = [
            ("550e8400-e29b-41d4-a716-446655440000", "uuid"),  # UUID
            ("12345", "numeric"),  # Numeric
            ("ABC123", "alphanumeric"),  # Alphanumeric
            ("user@example.com", "email"),  # Email
            ("https://example.com", "url"),  # URL
        ]

        for value, format_type in valid_formats:
            with self.subTest(value=value, format_type=format_type):
                result = self.validator._check_id_format(value, "TestColumn")
                self.assertIsNone(
                    result, f"Value '{value}' should be valid for {format_type}"
                )

    def test_check_id_format_invalid_formats(self) -> None:
        """Test ID format validation with invalid formats."""
        invalid_cases = [
            ("ab", "too short"),
            ("a" * 101, "too long"),
            ("ID with spaces", "contains whitespace"),
            ("ID@#$%", "contains special characters"),
        ]

        for value, reason in invalid_cases:
            with self.subTest(value=value, reason=reason):
                result = self.validator._check_id_format(value, "TestColumn")
                self.assertIsNotNone(
                    result, f"Value '{value}' should be invalid: {reason}"
                )

    def test_apply_id_fixes_duplicates(self) -> None:
        """Test fixing duplicate IDs by appending suffixes."""
        data = [
            ["ID", "Name"],  # Row 0 (header)
            ["001", "John"],  # Row 1
            ["002", "Jane"],  # Row 2
            ["001", "Bob"],  # Row 3 - Duplicate of Row 1
            ["003", "Alice"],  # Row 4
        ]

        validation_results = {
            "id_columns": [(0, "ID")],
            "duplicates": [
                {
                    "value": "001",
                    "rows": [
                        3,
                        5,
                    ],  # Row 3 and Row 5 both have "001" (based on row_idx + 2)
                    "column_name": "ID",
                    "issue": "duplicate_id",
                }
            ],
            "format_flags": [],
            "missing_ids": [],
            "suggestions": [],
        }

        fixed_data = self.validator._apply_id_fixes(data, validation_results)

        # Check that duplicate was fixed
        self.assertEqual(fixed_data[1][0], "001")  # First occurrence unchanged
        self.assertEqual(fixed_data[3][0], "001_001")  # Second occurrence gets suffix

    def test_apply_id_fixes_format_flags(self) -> None:
        """Test fixing format flags in IDs."""
        data = [
            ["ID", "Name"],
            ["001", "John"],
            ["ID with spaces", "Jane"],  # Format issue
            ["002", "Bob"],
        ]

        validation_results = {
            "id_columns": [(0, "ID")],
            "duplicates": [],
            "format_flags": [
                {
                    "row": 4,  # Row 3 (index 2) + 2 = 4
                    "col": 1,
                    "value": "ID with spaces",
                    "column_name": "ID",
                    "issue": "format_inconsistency",
                    "details": "ID contains whitespace",
                }
            ],
            "missing_ids": [],
            "suggestions": [],
        }

        fixed_data = self.validator._apply_id_fixes(data, validation_results)

        # Check that format issue was fixed
        self.assertEqual(
            fixed_data[2][0], "ID_with_spaces"
        )  # Spaces replaced with underscores

    def test_validate_integration(self) -> None:
        """Test the complete validation flow."""
        with patch.object(self.validator, "_get_spreadsheet") as mock_get_spreadsheet:
            mock_get_spreadsheet.return_value = self.mock_spreadsheet

            # Test flag mode
            result = self.validator.validate(
                "test.xlsx", mode="flag", auth_credentials=None
            )

            # Verify results structure
            self.assertIn("flags_found", result)
            self.assertIn("errors", result)
            self.assertIn("automated_log", result)

            # Should find flags (duplicates, missing IDs, format flags)
            self.assertGreater(result["flags_found"], 0)

    def test_validate_fix_mode(self) -> None:
        """Test validation in fix mode."""
        with patch.object(self.validator, "_get_spreadsheet") as mock_get_spreadsheet:
            mock_get_spreadsheet.return_value = self.mock_spreadsheet

            # Test fix mode
            result = self.validator.validate(
                "test.xlsx", mode="fix", auth_credentials=None
            )

            # Verify results structure
            self.assertIn("fixes_applied", result)
            self.assertIn("errors", result)
            self.assertIn("automated_log", result)

    def test_id_field_patterns(self) -> None:
        """Test that ID field patterns are properly defined."""
        self.assertIn("id_fields", ID_FIELD_PATTERNS)
        self.assertIn("id_formats", ID_FIELD_PATTERNS)

        # Check that patterns are valid regex
        for pattern in ID_FIELD_PATTERNS["id_fields"]:
            try:
                re.compile(pattern, re.IGNORECASE)
            except re.error as e:
                self.fail(f"Invalid regex pattern '{pattern}': {e}")

        for format_name, pattern in ID_FIELD_PATTERNS["id_formats"].items():
            try:
                re.compile(pattern, re.IGNORECASE)
            except re.error as e:
                self.fail(f"Invalid regex pattern for {format_name}: {e}")

    def test_empty_data_handling(self) -> None:
        """Test handling of empty data."""
        empty_data = []

        results = self.validator._identify_id_columns(empty_data)
        self.assertEqual(results, [])

        # Test with single header row
        single_header = ["ID"]
        results = self.validator._identify_id_columns(single_header)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], (0, "ID"))

    def test_custom_id_patterns(self) -> None:
        """Test custom ID pattern handling."""
        headers = ["CustomID", "Name", "OtherField"]
        custom_patterns = [r"^custom.*$", r"^other.*$"]

        id_columns = self.validator._identify_id_columns(headers, custom_patterns)

        expected_columns = [
            (0, "CustomID"),  # Matches custom pattern
            (2, "OtherField"),  # Matches other pattern
        ]

        self.assertEqual(id_columns, expected_columns)


if __name__ == "__main__":
    unittest.main()
