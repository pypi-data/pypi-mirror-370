"""Simple standalone tests for TabNameAlphanumeric functionality.

Tests the core sanitization logic without complex dependencies.
"""

import unittest
from urarovite.utils.tab_name_sanitizer import sanitize_tab_name


class TestTabNameAlphanumericCore(unittest.TestCase):
    """Test the core sanitization functionality."""

    def test_basic_valid_cases(self):
        """Test cases that should remain unchanged."""
        test_cases = [
            ("SimpleSheet", "SimpleSheet"),
            ("Sheet 1", "Sheet 1"),
            ("Sheet1", "Sheet1"),
            ("Data Analysis", "Data Analysis"),
            ("Report 2024", "Report 2024"),
        ]

        for input_name, expected in test_cases:
            with self.subTest(input_name=input_name):
                result = sanitize_tab_name(input_name)
                self.assertEqual(result, expected)

    def test_underscore_removal(self):
        """Test that underscores are converted to spaces (underscores are bad, spaces are good)."""
        test_cases = [
            ("Sheet_with_underscores", "Sheet with underscores"),
            ("Data_Analysis_Report", "Data Analysis Report"),
            ("Simple_Test", "Simple Test"),
            ("Multiple___Underscores", "Multiple Underscores"),  # Multiple underscores become spaces, then collapsed
        ]

        for input_name, expected in test_cases:
            with self.subTest(input_name=input_name):
                result = sanitize_tab_name(input_name)
                self.assertEqual(result, expected)

    def test_special_character_removal(self):
        """Test that special characters are omitted."""
        test_cases = [
            ("Sheet@#$%", "Sheet"),
            ("Data/Analysis", "DataAnalysis"),
            ("Report\\Final", "ReportFinal"),
            ("Test[Brackets]", "TestBrackets"),
            ("Sheet?Question", "SheetQuestion"),
            ("Data*Star", "DataStar"),
            ("Sheet|Pipe", "SheetPipe"),
            ("Mixed@#$_Test", "Mixed Test"),
        ]

        for input_name, expected in test_cases:
            with self.subTest(input_name=input_name):
                result = sanitize_tab_name(input_name)
                self.assertEqual(result, expected)

    def test_space_normalization(self):
        """Test that spaces are properly normalized."""
        test_cases = [
            ("Sheet   with   spaces", "Sheet with spaces"),
            ("   Leading and trailing   ", "Leading and trailing"),
            ("Multiple    Spaces    Here", "Multiple Spaces Here"),
            (
                "Mixed___and   spaces",
                "Mixed and spaces",
            ),  # Underscores converted to spaces, then collapsed with existing spaces
        ]

        for input_name, expected in test_cases:
            with self.subTest(input_name=input_name):
                result = sanitize_tab_name(input_name)
                self.assertEqual(result, expected)

    def test_edge_cases(self):
        """Test edge cases."""
        test_cases = [
            ("", "Sheet1"),  # Empty string
            ("   ", "Sheet1"),  # Only spaces
            ("@#$%", "Sheet1"),  # Only special chars
            ("___", "Sheet1"),  # Only underscores
            ("123Start", "Sheet 123Start"),  # Starts with number
            ("999", "Sheet 999"),  # Only numbers
        ]

        for input_name, expected in test_cases:
            with self.subTest(input_name=input_name):
                result = sanitize_tab_name(input_name)
                self.assertEqual(result, expected)

    def test_real_world_examples(self):
        """Test real-world examples."""
        test_cases = [
            ("Q1_2024_Sales_Report", "Q1 2024 Sales Report"),
            ("Data-Analysis_Final@Version", "DataAnalysis FinalVersion"),
            ("Marketing/Campaign[Results]", "MarketingCampaignResults"),
            ("Employee_Performance_Review_2024", "Employee Performance Review 2024"),
            ("Sheet_#1_with_lots_of_stuff!", "Sheet 1 with lots of stuff"),
        ]

        for input_name, expected in test_cases:
            with self.subTest(input_name=input_name):
                result = sanitize_tab_name(input_name)
                self.assertEqual(result, expected)

    def test_no_underscores_in_output(self):
        """Ensure underscores never appear in output (unless input was already clean)."""
        problematic_inputs = [
            "Sheet_with_underscores",
            "Data___Multiple___Underscores",
            "Mixed_@#$_Test",
            "___Only___Underscores___",
        ]

        for input_name in problematic_inputs:
            with self.subTest(input_name=input_name):
                result = sanitize_tab_name(input_name)
                # Result should not contain underscores
                self.assertNotIn(
                    "_", result, f"Result '{result}' should not contain underscores"
                )

    def test_spaces_preserved_when_appropriate(self):
        """Test that legitimate spaces are preserved."""
        test_cases = [
            ("Good Sheet Name", "Good Sheet Name"),
            ("Data Analysis 2024", "Data Analysis 2024"),
            ("Report Final Version", "Report Final Version"),
        ]

        for input_name, expected in test_cases:
            with self.subTest(input_name=input_name):
                result = sanitize_tab_name(input_name)
                self.assertEqual(result, expected)
                # Verify spaces are maintained
                self.assertIn(" ", result)


def run_tests():
    """Run all tests."""
    print("Running TabNameAlphanumeric Core Logic Tests")
    print("=" * 55)

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestTabNameAlphanumericCore)

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 55)
    if result.wasSuccessful():
        print(f"✅ All {result.testsRun} core logic tests passed!")
        print("\nKey changes verified:")
        print("- ✅ Underscores are converted to spaces for better readability")
        print("- ✅ Special characters are omitted (removed entirely)")
        print("- ✅ Spaces are supported and normalized")
        print("- ✅ Edge cases handled correctly")
    else:
        print(f"❌ {len(result.failures)} failures, {len(result.errors)} errors")
        for test, traceback in result.failures:
            print(f"\nFAILURE: {test}")
            print(traceback)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    import sys

    sys.exit(0 if success else 1)
