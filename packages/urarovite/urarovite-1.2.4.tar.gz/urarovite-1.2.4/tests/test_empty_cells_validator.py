"""Tests for the EmptyCellsValidator with target_ranges functionality."""

import unittest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List

from urarovite.validators.data_quality import EmptyCellsValidator
from urarovite.validators.base import ValidationResult
from urarovite.core.exceptions import ValidationError


class TestEmptyCellsValidator(unittest.TestCase):
    """Test cases for EmptyCellsValidator."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.validator = EmptyCellsValidator()
        self.mock_spreadsheet = Mock()
        self.mock_sheet_data = Mock()

        # Mock sheet data with some empty cells
        self.test_data = [
            ["A1", "B1", ""],  # Row 1: A1, B1, empty
            ["A2", "", "C2"],  # Row 2: A2, empty, C2
            ["", "B3", "C3"],  # Row 3: empty, B3, C3
            ["A4", "B4", "C4"],  # Row 4: all filled
        ]

        self.mock_sheet_data.values = self.test_data
        self.mock_sheet_data.sheet_name = "TestSheet"

        # Mock spreadsheet methods
        self.mock_spreadsheet.get_sheet_data.return_value = self.mock_sheet_data
        self.mock_spreadsheet.save.return_value = None

    def test_validate_all_cells_default_behavior(self) -> None:
        """Test that validator checks all cells when no target_ranges specified."""
        with patch.object(
            self.validator, "_get_spreadsheet", return_value=self.mock_spreadsheet
        ):
            with patch.object(self.validator, "_update_sheet_data"):
                result = self.validator.validate(
                    "test.xlsx", mode="flag", target_ranges=None
                )

        # Should find 3 empty cells
        self.assertEqual(result["flags_found"], 3)
        self.assertIn("empty_cells", result["details"])
        empty_cells = result["details"]["empty_cells"]
        self.assertEqual(len(empty_cells), 3)

        # Check specific empty cell positions
        expected_empty = [(1, 3), (2, 2), (3, 1)]  # 1-based indexing
        for pos in expected_empty:
            self.assertIn(pos, empty_cells)

    def test_validate_specific_range(self) -> None:
        """Test targeting a specific range of cells."""
        with patch.object(
            self.validator, "_get_spreadsheet", return_value=self.mock_spreadsheet
        ):
            with patch.object(self.validator, "_update_sheet_data"):
                result = self.validator.validate(
                    "test.xlsx", mode="flag", target_ranges="TestSheet!A1:C2"
                )

        # Should only find empty cells in the specified range
        self.assertEqual(result["flags_found"], 2)
        empty_cells = result["details"]["empty_cells"]
        self.assertEqual(len(empty_cells), 2)

        # Only cells in A1:C2 should be checked
        expected_empty = [(1, 3), (2, 2)]  # C1 and B2
        for pos in expected_empty:
            self.assertIn(pos, empty_cells)

    def test_validate_individual_cells(self) -> None:
        """Test targeting individual cells."""
        with patch.object(
            self.validator, "_get_spreadsheet", return_value=self.mock_spreadsheet
        ):
            with patch.object(self.validator, "_update_sheet_data"):
                result = self.validator.validate(
                    "test.xlsx",
                    mode="flag",
                    target_ranges=["TestSheet!A1", "TestSheet!B2", "TestSheet!C3"],
                )

        # Should only find empty cells in the specified individual cells
        self.assertEqual(result["flags_found"], 1)
        empty_cells = result["details"]["empty_cells"]
        self.assertEqual(len(empty_cells), 1)

        # Only B2 should be empty (A1 and C3 are filled)
        expected_empty = [(2, 2)]  # B2
        for pos in expected_empty:
            self.assertIn(pos, empty_cells)

    def test_validate_single_cell_string(self) -> None:
        """Test targeting a single cell as string."""
        with patch.object(
            self.validator, "_get_spreadsheet", return_value=self.mock_spreadsheet
        ):
            with patch.object(self.validator, "_update_sheet_data"):
                result = self.validator.validate(
                    "test.xlsx", mode="flag", target_ranges="TestSheet!B2"
                )

        # Should only find empty cell at B2
        self.assertEqual(result["flags_found"], 1)
        empty_cells = result["details"]["empty_cells"]
        self.assertEqual(len(empty_cells), 1)
        self.assertIn((2, 2), empty_cells)

    def test_validate_without_sheet_name(self) -> None:
        """Test targeting cells without specifying sheet name."""
        with patch.object(
            self.validator, "_get_spreadsheet", return_value=self.mock_spreadsheet
        ):
            with patch.object(self.validator, "_update_sheet_data"):
                result = self.validator.validate(
                    "test.xlsx", mode="flag", target_ranges="A1:C2"
                )

        # Should work with default sheet name
        self.assertEqual(result["flags_found"], 2)
        empty_cells = result["details"]["empty_cells"]
        self.assertEqual(len(empty_cells), 2)

    def test_validate_fix_mode_with_ranges(self) -> None:
        """Test fix mode with target ranges."""
        with patch.object(
            self.validator, "_get_spreadsheet", return_value=self.mock_spreadsheet
        ):
            with patch.object(self.validator, "_update_sheet_data") as mock_update:
                result = self.validator.validate(
                    "test.xlsx",
                    mode="fix",
                    target_ranges="TestSheet!A1:C2",
                    fill_value="FILLED",
                )

        # Should apply fixes
        self.assertEqual(result["fixes_applied"], 2)
        self.assertIn("fixed_cells", result["details"])

        # Should call update_sheet_data
        mock_update.assert_called_once()

    def test_invalid_range_format(self) -> None:
        """Test that invalid range formats raise ValidationError."""
        with patch.object(
            self.validator, "_get_spreadsheet", return_value=self.mock_spreadsheet
        ):
            with self.assertRaises(ValidationError):
                self.validator.validate(
                    "test.xlsx", mode="flag", target_ranges="InvalidRange"
                )

    def test_invalid_cell_reference(self) -> None:
        """Test that invalid cell references raise ValidationError."""
        with patch.object(
            self.validator, "_get_spreadsheet", return_value=self.mock_spreadsheet
        ):
            with self.assertRaises(ValidationError):
                self.validator.validate(
                    "test.xlsx", mode="flag", target_ranges="TestSheet!A"
                )

    def test_wrong_sheet_name(self) -> None:
        """Test that wrong sheet names raise ValidationError."""
        with patch.object(
            self.validator, "_get_spreadsheet", return_value=self.mock_spreadsheet
        ):
            with self.assertRaises(ValidationError):
                self.validator.validate(
                    "test.xlsx", mode="flag", target_ranges="WrongSheet!A1"
                )

    def test_range_parsing_edge_cases(self) -> None:
        """Test edge cases in range parsing."""
        # Test with quotes around sheet name
        with patch.object(
            self.validator, "_get_spreadsheet", return_value=self.mock_spreadsheet
        ):
            with patch.object(self.validator, "_update_sheet_data"):
                result = self.validator.validate(
                    "test.xlsx", mode="flag", target_ranges="'TestSheet'!A1"
                )

        self.assertEqual(result["flags_found"], 0)  # A1 is not empty

        # Test with double quotes
        with patch.object(
            self.validator, "_get_spreadsheet", return_value=self.mock_spreadsheet
        ):
            with patch.object(self.validator, "_update_sheet_data"):
                result = self.validator.validate(
                    "test.xlsx", mode="flag", target_ranges='"TestSheet"!A1'
                )

        self.assertEqual(result["flags_found"], 0)

    def test_column_letter_conversion(self) -> None:
        """Test column letter to index conversion."""
        # Test basic columns
        self.assertEqual(self.validator._column_letters_to_index("A"), 1)
        self.assertEqual(self.validator._column_letters_to_index("Z"), 26)
        self.assertEqual(self.validator._column_letters_to_index("AA"), 27)
        self.assertEqual(self.validator._column_letters_to_index("AZ"), 52)
        self.assertEqual(self.validator._column_letters_to_index("BA"), 53)

    def test_cell_reference_parsing(self) -> None:
        """Test cell reference parsing."""
        # Test valid references
        self.assertEqual(self.validator._parse_cell_reference("A1"), (1, 1))
        self.assertEqual(self.validator._parse_cell_reference("Z100"), (100, 26))
        self.assertEqual(self.validator._parse_cell_reference("AA1"), (1, 27))

        # Test invalid references
        with self.assertRaises(ValidationError):
            self.validator._parse_cell_reference("1A")
        with self.assertRaises(ValidationError):
            self.validator._parse_cell_reference("A")
        with self.assertRaises(ValidationError):
            self.validator._parse_cell_reference("1")

    def test_backward_compatibility(self) -> None:
        """Test that existing functionality still works without target_ranges."""
        with patch.object(
            self.validator, "_get_spreadsheet", return_value=self.mock_spreadsheet
        ):
            with patch.object(self.validator, "_update_sheet_data"):
                # Test without target_ranges parameter (old way)
                result = self.validator.validate("test.xlsx", mode="flag")

        # Should still find all empty cells
        self.assertEqual(result["flags_found"], 3)

        # Test with explicit None
        with patch.object(
            self.validator, "_get_spreadsheet", return_value=self.mock_spreadsheet
        ):
            with patch.object(self.validator, "_update_sheet_data"):
                result = self.validator.validate(
                    "test.xlsx", mode="flag", target_ranges=None
                )

        # Should still find all empty cells
        self.assertEqual(result["flags_found"], 3)


if __name__ == "__main__":
    unittest.main()
