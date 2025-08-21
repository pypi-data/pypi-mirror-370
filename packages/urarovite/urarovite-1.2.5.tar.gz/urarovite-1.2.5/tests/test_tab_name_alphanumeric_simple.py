"""Simple standalone tests for TabNameAlphanumeric functionality.

Tests the core sanitization logic without complex dependencies.
"""

import re
import unittest


def sanitize_tab_name(tab_name: str) -> str:
    """Copy of the sanitization logic from TabNameAlphanumericValidator."""
    if not tab_name:
        return "Sheet1"  # Default name for empty tab names

    # Keep only alphanumeric characters and spaces (omit all other chars)
    sanitized = re.sub(r"[^a-zA-Z0-9 ]", "", tab_name)

    # Collapse consecutive spaces to single space
    sanitized = re.sub(r" +", " ", sanitized)

    # Remove leading/trailing spaces
    sanitized = sanitized.strip()

    # Ensure the name isn't empty after sanitization
    if not sanitized:
        return "Sheet1"

    # Ensure it starts with a letter (not a number or space)
    if sanitized and sanitized[0].isdigit():
        sanitized = f"Sheet {sanitized}"

    return sanitized


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
        """Test that underscores are omitted (removed)."""
        test_cases = [
            ("Sheet_with_underscores", "Sheetwithunderscores"),
            ("Data_Analysis_Report", "DataAnalysisReport"),
            ("Simple_Test", "SimpleTest"),
            ("Multiple___Underscores", "MultipleUnderscores"),
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
            ("Mixed@#$_Test", "MixedTest"),
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
                "Mixedand spaces",
            ),  # Underscores omitted, spaces preserved
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
            ("Q1_2024_Sales_Report", "Q12024SalesReport"),
            ("Data-Analysis_Final@Version", "DataAnalysisFinalVersion"),
            ("Marketing/Campaign[Results]", "MarketingCampaignResults"),
            ("Employee_Performance_Review_2024", "EmployeePerformanceReview2024"),
            ("Sheet_#1_with_lots_of_stuff!", "Sheet1withlotsofstuff"),
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
        print("- ✅ Underscores are omitted (removed entirely)")
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
