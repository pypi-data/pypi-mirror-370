"""Simple test runner for TabNameValidator using built-in unittest.

This script runs TabNameValidator tests without requiring external dependencies.
"""

import sys
import unittest
from unittest.mock import Mock
import os

# Add the project root to the path so we can import urarovite modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from urarovite.validators.data_quality import (
        TabNameValidator,
        ILLEGAL_CHARS,
        EXCEL_MAX_TAB_NAME_LENGTH,
        MAX_BASE_NAME_LENGTH,
        COLLISION_SUFFIX_LENGTH,
    )
except ImportError as e:
    print(f"❌ Failed to import modules: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)


class TestTabNameValidator(unittest.TestCase):
    """Test suite for TabNameValidator using unittest."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.validator = TabNameValidator()

    def test_validator_initialization(self):
        """Test that the validator is properly initialized."""
        self.assertEqual(self.validator.id, "tab_names")
        self.assertEqual(self.validator.name, "Fix Tab Names")
        self.assertIn("illegal characters", self.validator.description)
        self.assertIn("Excel length limits", self.validator.description)

    def test_illegal_chars_constant(self):
        """Test that the illegal characters constant is properly defined."""
        expected_chars = ["\\", "/", "?", "*", "[", "]"]
        self.assertEqual(ILLEGAL_CHARS, expected_chars)

    def test_clean_tab_name_basic_replacement(self):
        """Test basic character replacement functionality."""
        test_cases = [
            ("Sheet\\with\\backslashes", "Sheet_with_backslashes"),
            ("Sheet/with/slashes", "Sheet_with_slashes"),
            ("Sheet?with?questions", "Sheet_with_questions"),
            ("Sheet*with*asterisks", "Sheet_with_asterisks"),
            ("Sheet[with[brackets]", "Sheet_with_brackets"),
            ("Sheet]with]brackets", "Sheet_with_brackets"),
        ]

        for input_name, expected in test_cases:
            with self.subTest(input_name=input_name):
                result = self.validator._clean_tab_name(input_name, "_")
                self.assertEqual(result, expected)

    def test_clean_tab_name_complex_cases(self):
        """Test complex character replacement scenarios."""
        test_cases = [
            ("Mix\\ed/Ch?ar*s[Test]", "Mix_ed_Ch_ar_s_Test"),
            ("___trimming___", "trimming"),
            ("Multiple___underscores", "Multiple_underscores"),
            ("", "Sheet"),  # empty case
            ("Normal_Sheet_Name", "Normal_Sheet_Name"),  # no illegal chars
            ("///", "Sheet"),  # all illegal chars
            ("_[]*_", "Sheet"),  # becomes empty after cleaning
        ]

        for input_name, expected in test_cases:
            with self.subTest(input_name=input_name):
                result = self.validator._clean_tab_name(input_name, "_")
                self.assertEqual(result, expected)

    def test_clean_tab_name_custom_replacement(self):
        """Test character replacement with custom replacement character."""
        input_name = "Sheet\\with/illegal*chars"
        result = self.validator._clean_tab_name(input_name, "-")
        self.assertEqual(result, "Sheet-with-illegal-chars")

        # Test with multiple consecutive custom chars
        input_name = "Test///Multiple"
        result = self.validator._clean_tab_name(input_name, "-")
        self.assertEqual(result, "Test-Multiple")

    def test_resolve_name_collision_no_conflict(self):
        """Test collision resolution when no conflict exists."""
        used_names = {"Sheet", "Data", "Summary"}
        result = self.validator._resolve_name_collision("NewSheet", used_names)
        self.assertEqual(result, "NewSheet")

    def test_resolve_name_collision_with_conflict(self):
        """Test collision resolution when conflicts exist."""
        used_names = {"Sheet", "Sheet_1", "Data", "Summary"}

        # Test first collision
        result = self.validator._resolve_name_collision("Data", used_names)
        self.assertEqual(result, "Data_1")

        # Test multiple collisions
        result = self.validator._resolve_name_collision("Sheet", used_names)
        self.assertEqual(result, "Sheet_2")

    def test_resolve_name_collision_progressive_numbering(self):
        """Test progressive numbering for multiple collisions."""
        used_names = {"Sheet", "Sheet_1", "Data", "Summary"}

        collision_tests = ["Sheet", "Data", "NewSheet", "Sheet", "Sheet"]
        expected_results = ["Sheet_2", "Data_1", "NewSheet", "Sheet_3", "Sheet_4"]

        for name, expected in zip(collision_tests, expected_results):
            with self.subTest(name=name):
                result = self.validator._resolve_name_collision(name, used_names)
                used_names.add(result)  # Add to used names for next iteration
                self.assertEqual(result, expected)

    def test_validate_no_sheets_error(self):
        """Test validation when spreadsheet has no sheets."""
        # Mock sheets service
        mock_service = Mock()
        mock_service.spreadsheets.return_value.get.return_value.execute.return_value = {
            "sheets": []
        }

        result = self.validator.validate(mock_service, "test_sheet_id", "flag")

        self.assertEqual(result["fixes_applied"], 0)
        self.assertEqual(result["flags_found"], 0)
        self.assertEqual(len(result["errors"]), 1)
        self.assertIn("No sheets found", result["errors"][0])

    def test_validate_no_illegal_characters(self):
        """Test validation when no illegal characters are found."""
        # Mock sheets service with clean tab names
        mock_service = Mock()
        mock_service.spreadsheets.return_value.get.return_value.execute.return_value = {
            "sheets": [
                {"properties": {"title": "Clean_Sheet_1", "sheetId": 0}},
                {"properties": {"title": "Clean_Sheet_2", "sheetId": 1}},
            ]
        }

        result = self.validator.validate(mock_service, "test_sheet_id", "flag")

        self.assertEqual(result["fixes_applied"], 0)
        self.assertEqual(result["flags_found"], 0)
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["details"], {})

    def test_edge_cases(self):
        """Test various edge cases."""
        # Test empty sheet name
        result = self.validator._clean_tab_name("", "_")
        self.assertEqual(result, "Sheet")

        # Test name with only illegal characters
        result = self.validator._clean_tab_name("\\/*[]", "_")
        self.assertEqual(result, "Sheet")

        # Test name with only replacement characters
        result = self.validator._clean_tab_name("___", "_")
        self.assertEqual(result, "Sheet")

        # Test very long name with illegal characters
        long_name = "Very" + "\\" * 50 + "Long" + "/" * 50 + "Name"
        result = self.validator._clean_tab_name(long_name, "_")
        self.assertEqual(result, "Very_Long_Name")
        self.assertFalse(any(char in result for char in ILLEGAL_CHARS))

    # ==================== Excel Length Limit Tests ====================

    def test_excel_constants(self):
        """Test that Excel-related constants are properly defined."""
        self.assertEqual(EXCEL_MAX_TAB_NAME_LENGTH, 31)
        self.assertEqual(COLLISION_SUFFIX_LENGTH, 5)
        self.assertEqual(MAX_BASE_NAME_LENGTH, 26)  # 31 - 5

    def test_generate_collision_suffix(self):
        """Test collision suffix generation."""
        # Test that suffix is 4 characters and consistent
        suffix1 = self.validator._generate_collision_suffix("TestName")
        suffix2 = self.validator._generate_collision_suffix("TestName")
        self.assertEqual(len(suffix1), 4)
        self.assertEqual(suffix1, suffix2)  # Should be deterministic
        self.assertTrue(suffix1.isupper())  # Should be uppercase

        # Test different names produce different suffixes
        suffix3 = self.validator._generate_collision_suffix("DifferentName")
        self.assertNotEqual(suffix1, suffix3)

    def test_truncate_for_excel_no_truncation_needed(self):
        """Test Excel truncation when name is already within limit."""
        short_name = "ShortName"
        used_names = set()
        result = self.validator._truncate_for_excel(short_name, used_names)
        self.assertEqual(result, short_name)
        self.assertLessEqual(len(result), EXCEL_MAX_TAB_NAME_LENGTH)

    def test_truncate_for_excel_simple_truncation(self):
        """Test simple Excel truncation without collision."""
        long_name = "This_is_a_very_long_tab_name_that_exceeds_Excel_limit"
        used_names = set()
        result = self.validator._truncate_for_excel(long_name, used_names)

        self.assertEqual(len(result), EXCEL_MAX_TAB_NAME_LENGTH)
        self.assertEqual(result, long_name[:EXCEL_MAX_TAB_NAME_LENGTH])
        self.assertTrue(result.startswith("This_is_a_very_long_tab_name_th"))

    def test_truncate_for_excel_with_collision(self):
        """Test Excel truncation when simple truncation would cause collision."""
        long_name = "This_is_a_very_long_tab_name_that_exceeds_Excel_limit"
        simple_truncated = long_name[:EXCEL_MAX_TAB_NAME_LENGTH]
        used_names = {simple_truncated}  # Collision!

        result = self.validator._truncate_for_excel(long_name, used_names)

        self.assertEqual(len(result), EXCEL_MAX_TAB_NAME_LENGTH)
        self.assertNotEqual(result, simple_truncated)
        self.assertNotIn(result, used_names)
        # Should end with collision suffix
        self.assertTrue("_" in result)
        suffix = result.split("_")[-1]
        self.assertEqual(len(suffix), 4)
        self.assertTrue(suffix.isupper())

    def test_truncate_for_excel_multiple_collisions(self):
        """Test Excel truncation with multiple collision attempts."""
        long_name = "This_is_a_very_long_tab_name_that_exceeds_Excel_limit"
        simple_truncated = long_name[:EXCEL_MAX_TAB_NAME_LENGTH]

        # Create collision scenario
        base_truncated = long_name[:MAX_BASE_NAME_LENGTH]
        suffix = self.validator._generate_collision_suffix(long_name)
        collision_name = f"{base_truncated}_{suffix}"

        used_names = {simple_truncated, collision_name}

        result = self.validator._truncate_for_excel(long_name, used_names)

        self.assertEqual(len(result), EXCEL_MAX_TAB_NAME_LENGTH)
        self.assertNotIn(result, used_names)

    def test_validate_excel_length_only_flag_mode(self):
        """Test validation with Excel length violations only in flag mode."""
        # Create mock data with long tab names but no illegal characters
        long_name_1 = "Very_Long_Tab_Name_That_Exceeds_Excel_31_Character_Limit_First"
        long_name_2 = "Another_Very_Long_Tab_Name_That_Also_Exceeds_Excel_Limit_Second"

        mock_service = Mock()
        mock_service.spreadsheets.return_value.get.return_value.execute.return_value = {
            "sheets": [
                {"properties": {"title": long_name_1, "sheetId": 0}},
                {"properties": {"title": long_name_2, "sheetId": 1}},
                {
                    "properties": {"title": "ShortName", "sheetId": 2}
                },  # This one is fine
            ]
        }

        result = self.validator.validate(mock_service, "test_sheet_id", "flag")

        self.assertEqual(result["fixes_applied"], 0)
        self.assertEqual(result["flags_found"], 2)  # Two long names
        self.assertEqual(result["errors"], [])

        # Check details
        self.assertIn("tab_flags", result["details"])
        flags = result["details"]["tab_flags"]
        self.assertEqual(len(flags), 2)

        # Verify issue types
        for issue in flags:
            self.assertIn("excel_length_limit", issue["issue_types"])
            self.assertNotIn("illegal_characters", issue["issue_types"])
            self.assertGreater(issue["original_length"], EXCEL_MAX_TAB_NAME_LENGTH)
            self.assertEqual(issue["fixed_length"], EXCEL_MAX_TAB_NAME_LENGTH)

    def test_validate_combined_flags_flag_mode(self):
        """Test validation with both illegal characters and Excel length violations."""
        problematic_name = "Very/Long*Tab[Name]That_Exceeds_Excel_31_Character_Limit_And_Has_Illegal_Chars"

        mock_service = Mock()
        mock_service.spreadsheets.return_value.get.return_value.execute.return_value = {
            "sheets": [
                {"properties": {"title": problematic_name, "sheetId": 0}},
                {"properties": {"title": "GoodName", "sheetId": 1}},
            ]
        }

        result = self.validator.validate(mock_service, "test_sheet_id", "flag")

        self.assertEqual(result["fixes_applied"], 0)
        self.assertEqual(result["flags_found"], 1)
        self.assertEqual(result["errors"], [])

        # Check that both issue types are detected
        issue = result["details"]["tab_flags"][0]
        self.assertIn("illegal_characters", issue["issue_types"])
        self.assertIn("excel_length_limit", issue["issue_types"])
        self.assertGreater(len(issue["illegal_chars"]), 0)
        self.assertGreater(issue["original_length"], EXCEL_MAX_TAB_NAME_LENGTH)
        self.assertEqual(issue["fixed_length"], EXCEL_MAX_TAB_NAME_LENGTH)

    def test_validate_excel_length_fix_mode(self):
        """Test validation with Excel length violations in fix mode."""
        long_name = "This_Is_A_Very_Long_Tab_Name_That_Definitely_Exceeds_Excel_Limit"

        mock_service = Mock()
        mock_service.spreadsheets.return_value.get.return_value.execute.return_value = {
            "sheets": [
                {"properties": {"title": long_name, "sheetId": 123}},
            ]
        }

        # Mock the batchUpdate call
        mock_service.spreadsheets.return_value.batchUpdate.return_value.execute.return_value = {}

        result = self.validator.validate(mock_service, "test_sheet_id", "fix")

        self.assertEqual(result["fixes_applied"], 1)
        self.assertEqual(result["flags_found"], 0)
        self.assertEqual(result["errors"], [])

        # Verify the batch update was called
        mock_service.spreadsheets.return_value.batchUpdate.assert_called_once()
        call_args = mock_service.spreadsheets.return_value.batchUpdate.call_args[1]

        # Check the update request
        body = call_args["body"]
        self.assertIn("requests", body)
        request = body["requests"][0]
        self.assertEqual(request["updateSheetProperties"]["properties"]["sheetId"], 123)

        new_title = request["updateSheetProperties"]["properties"]["title"]
        self.assertLessEqual(len(new_title), EXCEL_MAX_TAB_NAME_LENGTH)

    def test_excel_truncation_preserves_meaning(self):
        """Test that Excel truncation preserves as much meaning as possible."""
        test_cases = [
            ("Q1_2024_Sales_Report_Final_Version", "Q1_2024_Sales_Report_Final_Ve"),
            ("Marketing_Campaign_Analysis_Data", "Marketing_Campaign_Analysis_D"),
            ("Employee_Performance_Review_2024", "Employee_Performance_Review_2"),
        ]

        for long_name, expected_prefix in test_cases:
            with self.subTest(long_name=long_name):
                used_names = set()
                result = self.validator._truncate_for_excel(long_name, used_names)

                self.assertEqual(len(result), EXCEL_MAX_TAB_NAME_LENGTH)
                self.assertTrue(result.startswith(expected_prefix))

    def test_integration_illegal_chars_and_excel_length(self):
        """Test integration of illegal character cleaning and Excel length truncation."""
        # Name with both flags: illegal chars + too long
        problematic_name = (
            "Q1/2024*Sales[Report]Final_Version_That_Exceeds_Excel_Character_Limit"
        )

        used_names = set()

        # Step 1: Clean illegal characters
        cleaned = self.validator._clean_tab_name(problematic_name, "_")
        self.assertFalse(any(char in cleaned for char in ILLEGAL_CHARS))

        # Step 2: Handle Excel length if needed
        if len(cleaned) > EXCEL_MAX_TAB_NAME_LENGTH:
            final_result = self.validator._truncate_for_excel(cleaned, used_names)
        else:
            final_result = cleaned

        # Final result should be safe
        self.assertLessEqual(len(final_result), EXCEL_MAX_TAB_NAME_LENGTH)
        self.assertFalse(any(char in final_result for char in ILLEGAL_CHARS))

        # Should still contain meaningful parts
        self.assertIn("Q1", final_result)
        self.assertIn("2024", final_result)


def run_tests():
    """Run all the tests and provide a summary."""
    print("Running TabNameValidator Tests")
    print("=" * 50)

    # Create a test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestTabNameValidator)

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
